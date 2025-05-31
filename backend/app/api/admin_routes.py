from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from app.db.mongo_db import MongoDBManager
from app.utils.file_utils import save_uploaded_file, delete_subject_files, allowed_file
from app.core.syllabus_processor import (
    parse_admin_syllabus_form, 
    process_syllabus_for_embedding,
    validate_syllabus_data
)
from app.core.textbook_processor import process_textbook_pdf, validate_pdf_file
from app.core.embedding_manager import build_and_save_faiss_indexes_for_subject

admin_bp = Blueprint('admin', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

@admin_bp.route('/subjects', methods=['POST'])
def create_subject():
    """Create a new subject."""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Subject name is required'}), 400
        
        subject_name = data['name'].strip()
        if not subject_name:
            return jsonify({'error': 'Subject name cannot be empty'}), 400
        
        # Check if subject already exists
        existing_subject = MongoDBManager.get_subject_by_name(subject_name)
        if existing_subject:
            return jsonify({'error': 'Subject with this name already exists'}), 409
        
        # Create subject
        subject_id = MongoDBManager.add_subject(subject_name)
        
        return jsonify({
            'success': True,
            'subject_id': subject_id,
            'message': f'Subject "{subject_name}" created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to create subject: {str(e)}'}), 500

@admin_bp.route('/subjects', methods=['GET'])
def list_subjects():
    """List all subjects."""
    try:
        subjects = MongoDBManager.list_subjects()
        return jsonify({
            'success': True,
            'subjects': subjects
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve subjects: {str(e)}'}), 500

@admin_bp.route('/subjects/<subject_id>', methods=['GET'])
def get_subject(subject_id):
    """Get subject details."""
    try:
        subject = MongoDBManager.get_subject_by_id(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        return jsonify({
            'success': True,
            'subject': subject
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve subject: {str(e)}'}), 500

@admin_bp.route('/subjects/<subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    """Delete a subject and all associated data."""
    try:
        # Check if subject exists
        subject = MongoDBManager.get_subject_by_id(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        # Delete files
        delete_subject_files(subject_id, current_app.config['UPLOAD_FOLDER'])
        
        # Delete FAISS indexes
        faiss_folder = current_app.config['FAISS_INDEX_FOLDER']
        subject_faiss_folder = os.path.join(faiss_folder, subject_id)
        if os.path.exists(subject_faiss_folder):
            import shutil
            shutil.rmtree(subject_faiss_folder)
        
        # Delete from database
        success = MongoDBManager.delete_subject_data(subject_id)
        if not success:
            return jsonify({'error': 'Failed to delete subject from database'}), 500
        
        return jsonify({
            'success': True,
            'message': f'Subject "{subject["name"]}" deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to delete subject: {str(e)}'}), 500

@admin_bp.route('/subjects/<subject_id>/syllabus', methods=['POST'])
def upload_syllabus(subject_id):
    """Upload syllabus data for a subject."""
    try:
        # Check if subject exists
        subject = MongoDBManager.get_subject_by_id(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        # Get form data
        form_data = request.get_json()
        if not form_data:
            return jsonify({'error': 'No syllabus data provided'}), 400
        
        # Parse syllabus form data
        syllabus_json = parse_admin_syllabus_form(form_data)
        
        # Validate syllabus data
        validation_errors = validate_syllabus_data(syllabus_json)
        if validation_errors:
            return jsonify({
                'error': 'Invalid syllabus data',
                'validation_errors': validation_errors
            }), 400
        
        # Save syllabus to MongoDB
        success = MongoDBManager.update_subject_syllabus(subject_id, syllabus_json)
        if not success:
            return jsonify({'error': 'Failed to save syllabus'}), 500
        
        # Process syllabus for embedding
        syllabus_docs = process_syllabus_for_embedding(syllabus_json)
        
        # Get existing textbook documents
        textbook_docs = []
        textbooks = MongoDBManager.get_textbooks_for_subject(subject_id)
        for textbook in textbooks:
            textbook_path = textbook.get('stored_filepath')
            if textbook_path and os.path.exists(textbook_path):
                docs = process_textbook_pdf(textbook_path)
                textbook_docs.extend(docs)
        
        # Build and save FAISS indexes
        embedding_success = build_and_save_faiss_indexes_for_subject(
            subject_id, syllabus_docs, textbook_docs
        )
        
        response_data = {
            'success': True,
            'message': 'Syllabus uploaded successfully',
            'units_processed': len(syllabus_json.get('units', [])),
            'documents_created': len(syllabus_docs)
        }
        
        if not embedding_success:
            response_data['warning'] = 'Syllabus saved but embedding generation failed'
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Failed to upload syllabus: {str(e)}'}), 500

@admin_bp.route('/subjects/<subject_id>/textbooks', methods=['POST'])
def upload_textbooks(subject_id):
    """Upload textbook PDF files for a subject."""
    try:
        # Check if subject exists
        subject = MongoDBManager.get_subject_by_id(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        # Check if files were uploaded
        if 'files' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('files')
        if not files or all(file.filename == '' for file in files):
            return jsonify({'error': 'No files selected'}), 400
        
        uploaded_files = []
        processing_errors = []
        
        for file in files:
            if file and file.filename:
                # Check file extension
                if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
                    processing_errors.append(f'{file.filename}: Only PDF files are allowed')
                    continue
                
                try:
                    # Save file
                    file_path = save_uploaded_file(
                        file, subject_id, 'textbooks', current_app.config['UPLOAD_FOLDER']
                    )
                    
                    # Validate PDF
                    pdf_validation = validate_pdf_file(file_path)
                    if not pdf_validation['is_valid']:
                        processing_errors.append(f'{file.filename}: {pdf_validation.get("error", "Invalid PDF")}')
                        os.remove(file_path)  # Clean up invalid file
                        continue
                    
                    # Save metadata to MongoDB
                    success = MongoDBManager.add_textbook_to_subject(
                        subject_id, 
                        secure_filename(file.filename), 
                        file_path, 
                        file.filename
                    )
                    
                    if success:
                        uploaded_files.append({
                            'filename': file.filename,
                            'size_mb': round(pdf_validation['file_size_mb'], 2),
                            'pages': pdf_validation['page_count']
                        })
                    else:
                        processing_errors.append(f'{file.filename}: Failed to save metadata')
                        os.remove(file_path)  # Clean up
                        
                except Exception as e:
                    processing_errors.append(f'{file.filename}: {str(e)}')
        
        # If any files were successfully uploaded, regenerate embeddings
        if uploaded_files:
            try:
                # Get syllabus documents
                syllabus_docs = []
                syllabus = MongoDBManager.get_syllabus_for_subject(subject_id)
                if syllabus:
                    syllabus_docs = process_syllabus_for_embedding(syllabus)
                
                # Get all textbook documents
                textbook_docs = []
                textbooks = MongoDBManager.get_textbooks_for_subject(subject_id)
                for textbook in textbooks:
                    textbook_path = textbook.get('stored_filepath')
                    if textbook_path and os.path.exists(textbook_path):
                        docs = process_textbook_pdf(textbook_path)
                        textbook_docs.extend(docs)
                
                # Build and save FAISS indexes
                embedding_success = build_and_save_faiss_indexes_for_subject(
                    subject_id, syllabus_docs, textbook_docs
                )
                
                if not embedding_success:
                    processing_errors.append("Embedding generation failed")
                    
            except Exception as e:
                processing_errors.append(f"Embedding generation error: {str(e)}")
        
        response_data = {
            'success': len(uploaded_files) > 0,
            'uploaded_files': uploaded_files,
            'files_uploaded': len(uploaded_files),
            'total_files': len(files)
        }
        
        if processing_errors:
            response_data['errors'] = processing_errors
        
        if uploaded_files:
            response_data['message'] = f'{len(uploaded_files)} textbook(s) uploaded successfully'
        else:
            response_data['error'] = 'No files were successfully uploaded'
            return jsonify(response_data), 400
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Failed to upload textbooks: {str(e)}'}), 500

@admin_bp.route('/subjects/<subject_id>/regenerate-embeddings', methods=['POST'])
def regenerate_embeddings(subject_id):
    """Manually regenerate embeddings for a subject."""
    try:
        # Check if subject exists
        subject = MongoDBManager.get_subject_by_id(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        # Get syllabus documents
        syllabus_docs = []
        syllabus = MongoDBManager.get_syllabus_for_subject(subject_id)
        if syllabus:
            syllabus_docs = process_syllabus_for_embedding(syllabus)
        
        # Get textbook documents
        textbook_docs = []
        textbooks = MongoDBManager.get_textbooks_for_subject(subject_id)
        for textbook in textbooks:
            textbook_path = textbook.get('stored_filepath')
            if textbook_path and os.path.exists(textbook_path):
                docs = process_textbook_pdf(textbook_path)
                textbook_docs.extend(docs)
        
        if not syllabus_docs and not textbook_docs:
            return jsonify({'error': 'No content available for embedding generation'}), 400
        
        # Build and save FAISS indexes
        success = build_and_save_faiss_indexes_for_subject(
            subject_id, syllabus_docs, textbook_docs
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Embeddings regenerated successfully',
                'syllabus_documents': len(syllabus_docs),
                'textbook_documents': len(textbook_docs)
            })
        else:
            return jsonify({'error': 'Failed to regenerate embeddings'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to regenerate embeddings: {str(e)}'}), 500
