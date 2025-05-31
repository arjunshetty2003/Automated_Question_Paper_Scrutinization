#!/usr/bin/env python3
"""
Script to initialize the admin user and set up the database.
Run this script once after setting up the backend.
"""

import os
import sys
from werkzeug.security import generate_password_hash

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.mongo_db import MongoDBManager
from config import Config

def create_admin_user():
    """Create the default admin user"""
    db_manager = MongoDBManager()
    
    # Check if admin user already exists
    existing_admin = db_manager.users.find_one({'username': 'admin'})
    if existing_admin:
        print("Admin user already exists!")
        return
    
    # Create admin user
    admin_user = {
        'username': 'admin',
        'email': 'admin@questionpaper.com',
        'password_hash': generate_password_hash('admin123'),
        'full_name': 'System Administrator',
        'role': 'admin',
        'is_active': True
    }
    
    try:
        result = db_manager.create_user(admin_user)
        print(f"Admin user created successfully with ID: {result.inserted_id}")
        print("Login credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nPlease change the password after first login!")
    except Exception as e:
        print(f"Error creating admin user: {e}")

def setup_indexes():
    """Create database indexes for better performance"""
    db_manager = MongoDBManager()
    
    try:
        # Create indexes
        db_manager.users.create_index([('username', 1)], unique=True)
        db_manager.users.create_index([('email', 1)], unique=True)
        db_manager.subjects.create_index([('code', 1)], unique=True)
        print("Database indexes created successfully!")
    except Exception as e:
        print(f"Error creating indexes: {e}")

def main():
    """Main initialization function"""
    print("Initializing Question Paper Scrutinization System...")
    print("=" * 50)
    
    # Check if MongoDB connection works
    try:
        db_manager = MongoDBManager()
        db_manager.db.command('ping')
        print("✓ MongoDB connection successful")
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        print("Please ensure MongoDB is running and the connection string is correct.")
        return
    
    # Setup database indexes
    setup_indexes()
    
    # Create admin user
    create_admin_user()
    
    print("\n" + "=" * 50)
    print("Initialization complete!")
    print("\nNext steps:")
    print("1. Start the backend server: python run.py")
    print("2. Start the frontend server: cd frontend && npm run dev")
    print("3. Access the application at http://localhost:5173")
    print("4. Login with admin credentials to begin setup")

if __name__ == '__main__':
    main()
