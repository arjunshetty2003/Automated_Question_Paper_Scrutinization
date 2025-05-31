from flask import Blueprint, request, jsonify, current_app
import os
from app.db.mongo_db import MongoDBManager
from app.utils.file_utils import save_uploaded_file, allowed_file
from app.core.qp_pdf_parser import parse_question_paper_pdf, validate_question_paper_structure
from app.core.validation_engine import validate_question_paper

user_bp = Blueprint('user', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

@user_bp.route('/subjects', methods=['GET'])
def get_subjects():
    """Get list of all subjects for teacher dropdown."""
    try:
        subjects = MongoDBManager.list_subjects()
        
        # Return simplified subject list for dropdown
        subject_list = []
        for subject in subjects:
            subject_info = {
                'id': subject['_id'],
                'name': subject['name'],
                'has_syllabus': subject.get('syllabus') is not None,
                'textbook_count': len(subject.get('textbooks', []))
            }
            subject_list.append(subject_info)
        
        return jsonify({
            'success': True,
            'subjects': subject_list
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve subjects: {str(e)}'}), 500

@user_bp.route('/subjects/<subject_id>/info', methods=['GET'])
def get_subject_info(subject_id):
    """Get detailed information about a subject."""
    try:
        subject = MongoDBManager.get_subject_by_id(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        # Get additional information
        textbooks = MongoDBManager.get_textbooks_for_subject(subject_id)
        syllabus = MongoDBManager.get_syllabus_for_subject(subject_id)
        
        subject_info = {
            'id': subject['_id'],
            'name': subject['name'],
            'created_at': subject.get('created_at'),
            'has_syllabus': syllabus is not None,
            'syllabus_units': len(syllabus.get('units', [])) if syllabus else 0,
            'textbook_count': len(textbooks),
            'textbooks': [
                {
                    'filename': tb.get('original_filename', tb.get('filename')),
                    'uploaded_at': tb.get('uploaded_at')
                } for tb in textbooks
            ],
            'has_embeddings': {
                'syllabus': MongoDBManager.get_faiss_index_path(subject_id, 'syllabus') is not None,
                'textbook': MongoDBManager.get_faiss_index_path(subject_id, 'textbook') is not None
            }
        }
        
        return jsonify({
            'success': True,
            'subject': subject_info
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve subject info: {str(e)}'}), 500

@user_bp.route('/validate/question-paper/<subject_id>', methods=['POST'])
def validate_question_paper_route(subject_id):
    """Upload and validate a question paper for a subject."""
    try:
        # Check if subject exists
        subject = MongoDBManager.get_subject_by_id(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Save uploaded file
        file_path = save_uploaded_file(
            file, subject_id, 'question_papers', current_app.config['UPLOAD_FOLDER']
        )
        
        try:
            # Parse question paper PDF
            course_name = subject.get('name', '')
            parsed_questions = parse_question_paper_pdf(file_path, course_name)
            
            if not parsed_questions:
                return jsonify({
                    'error': 'Failed to parse question paper. Please ensure the PDF contains readable text and follows standard question paper format.'
                }), 400
            
            # Validate question paper structure
            structure_validation = validate_question_paper_structure(parsed_questions)
            
            if not structure_validation['is_valid']:
                return jsonify({
                    'error': 'Invalid question paper structure',
                    'details': structure_validation
                }), 400
            
            # Perform content validation
            validation_results = validate_question_paper(parsed_questions, subject_id)
            
            if not validation_results['success']:
                return jsonify({
                    'error': validation_results.get('error', 'Validation failed'),
                    'parsed_questions': len(parsed_questions)
                }), 400
            
            # Clean up uploaded file (optional - you might want to keep it for audit)
            try:
                os.remove(file_path)
            except:
                pass  # Ignore cleanup errors
            
            return jsonify({
                'success': True,
                'message': 'Question paper validated successfully',
                'validation_results': validation_results,
                'parsing_info': {
                    'total_questions': len(parsed_questions),
                    'structure_validation': structure_validation
                }
            })
            
        except Exception as validation_error:
            # Clean up uploaded file on error
            try:
                os.remove(file_path)
            except:
                pass
            
            return jsonify({
                'error': f'Validation failed: {str(validation_error)}'
            }), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to process question paper: {str(e)}'}), 500

@user_bp.route('/validate/preview/<subject_id>', methods=['POST'])
def preview_question_paper(subject_id):
    """Preview parsed questions from uploaded question paper without full validation."""
    try:
        # Check if subject exists
        subject = MongoDBManager.get_subject_by_id(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Save uploaded file temporarily
        file_path = save_uploaded_file(
            file, subject_id, 'temp', current_app.config['UPLOAD_FOLDER']
        )
        
        try:
            # Parse question paper PDF
            course_name = subject.get('name', '')
            parsed_questions = parse_question_paper_pdf(file_path, course_name)
            
            # Validate structure
            structure_validation = validate_question_paper_structure(parsed_questions)
            
            # Clean up temp file
            try:
                os.remove(file_path)
            except:
                pass
            
            return jsonify({
                'success': True,
                'parsed_questions': parsed_questions,
                'structure_validation': structure_validation,
                'preview_info': {
                    'total_questions': len(parsed_questions),
                    'filename': file.filename,
                    'subject_name': subject.get('name', '')
                }
            })
            
        except Exception as parsing_error:
            # Clean up temp file
            try:
                os.remove(file_path)
            except:
                pass
            
            return jsonify({
                'error': f'Failed to parse question paper: {str(parsing_error)}'
            }), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to preview question paper: {str(e)}'}), 500

@user_bp.route('/validation-history', methods=['GET'])
def get_validation_history():
    """Get validation history (if you implement history tracking)."""
    # This would require additional database schema to track validation history
    # For now, return a placeholder response
    return jsonify({
        'success': True,
        'message': 'Validation history feature not yet implemented',
        'history': []
    })

@user_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get general statistics about the system."""
    try:
        subjects = MongoDBManager.list_subjects()
        
        stats = {
            'total_subjects': len(subjects),
            'subjects_with_syllabus': sum(1 for s in subjects if s.get('syllabus')),
            'subjects_with_textbooks': sum(1 for s in subjects if s.get('textbooks')),
            'total_textbooks': sum(len(s.get('textbooks', [])) for s in subjects)
        }
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve statistics: {str(e)}'}), 500
