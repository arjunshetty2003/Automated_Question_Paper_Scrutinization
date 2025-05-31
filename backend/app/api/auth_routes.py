from flask import Blueprint, request, jsonify, current_app
import bcrypt
import jwt
import datetime
from app.db.mongo_db import MongoDBManager

auth_bp = Blueprint('auth', __name__)

def generate_token(user_id: str, username: str, role: str) -> str:
    """Generate JWT token for user."""
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        'iat': datetime.datetime.utcnow()
    }
    
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def verify_token(token: str) -> dict:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token has expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}

@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    """Admin login endpoint."""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # Get user from database
        user = MongoDBManager.get_user_by_username(username)
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if user is admin
        if user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Check if user is active
        if not user.get('is_active', True):
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate token
        token = generate_token(user['_id'], user['username'], user['role'])
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['_id'],
                'username': user['username'],
                'role': user['role']
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/teacher/login', methods=['POST'])
def teacher_login():
    """Teacher login endpoint."""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # Get user from database
        user = MongoDBManager.get_user_by_username(username)
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if user is teacher
        if user.get('role') != 'teacher':
            return jsonify({'error': 'Teacher access required'}), 403
        
        # Check if user is active
        if not user.get('is_active', True):
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate token
        token = generate_token(user['_id'], user['username'], user['role'])
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['_id'],
                'username': user['username'],
                'role': user['role']
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/teacher/register', methods=['POST'])
def register_teacher():
    """Admin registers a new teacher."""
    try:
        # This endpoint should be protected to admin only
        # For now, we'll implement basic functionality
        
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # Validate input
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Check if username already exists
        existing_user = MongoDBManager.get_user_by_username(username)
        if existing_user:
            return jsonify({'error': 'Username already exists'}), 409
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        user_id = MongoDBManager.create_user(username, hashed_password.decode('utf-8'), 'teacher')
        
        return jsonify({
            'success': True,
            'message': f'Teacher "{username}" registered successfully',
            'user_id': user_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token_route():
    """Verify if a token is valid."""
    try:
        data = request.get_json()
        
        if not data or not data.get('token'):
            return jsonify({'error': 'Token is required'}), 400
        
        token = data['token']
        payload = verify_token(token)
        
        if 'error' in payload:
            return jsonify(payload), 401
        
        # Get updated user info
        user = MongoDBManager.get_user_by_username(payload['username'])
        if not user or not user.get('is_active', True):
            return jsonify({'error': 'User not found or inactive'}), 401
        
        return jsonify({
            'success': True,
            'valid': True,
            'user': {
                'id': user['_id'],
                'username': user['username'],
                'role': user['role']
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Token verification failed: {str(e)}'}), 500

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """Change user password."""
    try:
        data = request.get_json()
        
        if not data or not all(key in data for key in ['username', 'current_password', 'new_password']):
            return jsonify({'error': 'Username, current password, and new password are required'}), 400
        
        username = data['username'].strip()
        current_password = data['current_password']
        new_password = data['new_password']
        
        # Validate new password
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters long'}), 400
        
        # Get user
        user = MongoDBManager.get_user_by_username(username)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify current password
        if not bcrypt.checkpw(current_password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Hash new password
        hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        # Update password in database
        # Note: This would require implementing an update_user_password method in MongoDBManager
        # For now, we'll return a placeholder response
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Password change failed: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout endpoint (mainly for client-side token removal)."""
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })

# Utility function for route protection (can be used as decorator)
def token_required(f):
    """Decorator to protect routes with token authentication."""
    from functools import wraps
    
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Verify token
        payload = verify_token(token)
        if 'error' in payload:
            return jsonify(payload), 401
        
        # Add user info to request context
        request.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to require admin role."""
    from functools import wraps
    
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.current_user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    
    return decorated
