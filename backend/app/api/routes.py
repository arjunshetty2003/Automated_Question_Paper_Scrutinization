import os
import uuid
import json
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from bson import ObjectId
from ..models.db_models import Syllabus, Textbook, QuestionPaper, ValidationResult
from ..utils.pdf_utils import load_syllabus_from_json, prepare_textbook_documents, load_question_paper_from_json
from ..core.vector_store import create_syllabus_vector_store, create_textbook_vector_store, get_vector_store_path, check_vector_store_exists
from ..core.validation import validate_question_paper

api = Blueprint('api', __name__)

# Helper function to make MongoDB documents JSON serializable
def serialize_doc(doc):
    if doc is None:
        return None
        
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
        
    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, list) or isinstance(value, dict):
                result[key] = serialize_doc(value)
            else:
                result[key] = value
        return result
        
    return doc

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "API is up and running"})

@api.route('/syllabus', methods=['POST'])
def upload_syllabus():
    """Upload a syllabus JSON file"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if not allowed_file(file.filename, {'json'}):
        return jsonify({"error": "Only JSON files are allowed"}), 400
    
    # Create a safe filename
    filename = secure_filename(file.filename)
    unique_id = str(uuid.uuid4())
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'syllabus', f"{unique_id}_{filename}")
    
    # Save the file
    file.save(file_path)
    
    # Process the syllabus file
    try:
        documents, syllabus_data = load_syllabus_from_json(file_path)
        
        if not documents or not syllabus_data:
            return jsonify({"error": "Invalid syllabus format or empty syllabus"}), 400
            
        # Save to database
        syllabus = Syllabus.create(
            user_id=None,  # No authentication in this simple version
            name=filename,
            file_path=file_path,
            course_name=syllabus_data.get("course_name", "Unknown Course"),
            units=syllabus_data.get("units", []),
            vectorized=False
        )
        
        # Create vector store
        success, message = create_syllabus_vector_store(str(syllabus['_id']), file_path, None)
        
        if not success:
            return jsonify({"error": f"Failed to create vector store: {message}"}), 500
            
        return jsonify({
            "success": True,
            "message": "Syllabus uploaded and processed successfully",
            "syllabus_id": str(syllabus['_id']),
            "course_name": syllabus_data.get("course_name", "Unknown Course"),
            "units_count": len(syllabus_data.get("units", []))
        })
        
    except Exception as e:
        return jsonify({"error": f"Error processing syllabus: {str(e)}"}), 500

@api.route('/textbook', methods=['POST'])
def upload_textbook():
    """Upload a textbook PDF file"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    syllabus_id = request.form.get('syllabus_id')
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if not allowed_file(file.filename, {'pdf'}):
        return jsonify({"error": "Only PDF files are allowed"}), 400
    
    # Create a safe filename
    filename = secure_filename(file.filename)
    unique_id = str(uuid.uuid4())
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'textbooks', f"{unique_id}_{filename}")
    
    # Save the file
    file.save(file_path)
    
    # Save to database
    textbook = Textbook.create(
        user_id=None,  # No authentication in this simple version
        name=filename,
        file_path=file_path,
        syllabus_id=syllabus_id,
        vectorized=False
    )
    
    # Create vector store
    try:
        success, message = create_textbook_vector_store(str(textbook['_id']), file_path, None)
        
        if not success:
            return jsonify({"error": f"Failed to create vector store: {message}"}), 500
            
        return jsonify({
            "success": True,
            "message": "Textbook uploaded and processed successfully",
            "textbook_id": str(textbook['_id']),
            "name": filename
        })
        
    except Exception as e:
        return jsonify({"error": f"Error processing textbook: {str(e)}"}), 500

@api.route('/question-paper', methods=['POST'])
def upload_question_paper():
    """Upload a question paper JSON file"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    syllabus_id = request.form.get('syllabus_id')
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if not allowed_file(file.filename, {'json'}):
        return jsonify({"error": "Only JSON files are allowed"}), 400
    
    # Create a safe filename
    filename = secure_filename(file.filename)
    unique_id = str(uuid.uuid4())
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'question_papers', f"{unique_id}_{filename}")
    
    # Save the file
    file.save(file_path)
    
    # Process the question paper file
    try:
        questions = load_question_paper_from_json(file_path)
        
        if not questions:
            return jsonify({"error": "Invalid question paper format or empty question paper"}), 400
            
        # Save to database
        question_paper = QuestionPaper.create(
            user_id=None,  # No authentication in this simple version
            name=filename,
            file_path=file_path,
            syllabus_id=syllabus_id,
            questions=questions
        )
        
        return jsonify({
            "success": True,
            "message": "Question paper uploaded successfully",
            "question_paper_id": str(question_paper['_id']),
            "questions_count": len(questions)
        })
        
    except Exception as e:
        return jsonify({"error": f"Error processing question paper: {str(e)}"}), 500

@api.route('/validate', methods=['POST'])
def validate():
    """Validate a question paper against syllabus and textbooks"""
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    question_paper_id = data.get('question_paper_id')
    syllabus_id = data.get('syllabus_id')
    textbook_ids = data.get('textbook_ids', [])
    
    if not question_paper_id or not syllabus_id:
        return jsonify({"error": "Question paper ID and syllabus ID are required"}), 400
    
    # Check if resources exist
    question_paper = QuestionPaper.find_by_id(question_paper_id)
    if not question_paper:
        return jsonify({"error": "Question paper not found"}), 404
        
    syllabus = Syllabus.find_by_id(syllabus_id)
    if not syllabus:
        return jsonify({"error": "Syllabus not found"}), 404
    
    # Check if vector stores exist
    syllabus_vs_path = get_vector_store_path('syllabus', syllabus_id)
    if not check_vector_store_exists('syllabus', syllabus_id):
        return jsonify({"error": "Syllabus vector store not found. Please process the syllabus first."}), 400
    
    # Get paths to textbook vector stores
    textbook_vs_paths = []
    for textbook_id in textbook_ids:
        if check_vector_store_exists('textbook', textbook_id):
            textbook_vs_paths.append(get_vector_store_path('textbook', textbook_id))
    
    # Run validation
    try:
        validation_results = validate_question_paper(
            question_paper['questions'],
            syllabus_vs_path,
            textbook_vs_paths,
            current_app.config.get('GEMINI_API_KEY')
        )
        
        # Save results to database
        result = ValidationResult.create(
            user_id=None,  # No authentication in this simple version
            question_paper_id=question_paper_id,
            syllabus_id=syllabus_id,
            textbook_ids=textbook_ids,
            validation_summary=validation_results['validation_summary'],
            errors=validation_results['errors_encountered']
        )
        
        return jsonify({
            "success": True,
            "message": "Validation completed successfully",
            "result_id": str(result['_id']),
            "results": validation_results
        })
        
    except Exception as e:
        return jsonify({"error": f"Error during validation: {str(e)}"}), 500

@api.route('/results/<result_id>', methods=['GET'])
def get_validation_result(result_id):
    """Get a validation result by ID"""
    result = ValidationResult.find_by_id(result_id)
    
    if not result:
        return jsonify({"error": "Validation result not found"}), 404
        
    return jsonify({
        "success": True,
        "result": serialize_doc(result)
    })

@api.route('/syllabus/all', methods=['GET'])
def get_all_syllabi():
    """Get all syllabi"""
    syllabi = Syllabus.find_by_user(None)
    
    return jsonify({
        "success": True,
        "syllabi": serialize_doc(syllabi)
    })

@api.route('/textbooks/all', methods=['GET'])
def get_all_textbooks():
    """Get all textbooks"""
    textbooks = Textbook.find_by_user(None)
    
    return jsonify({
        "success": True,
        "textbooks": serialize_doc(textbooks)
    })

@api.route('/question-papers/all', methods=['GET'])
def get_all_question_papers():
    """Get all question papers"""
    question_papers = QuestionPaper.find_by_user(None)
    
    return jsonify({
        "success": True,
        "question_papers": serialize_doc(question_papers)
    })

@api.route('/results/all', methods=['GET'])
def get_all_results():
    """Get all validation results"""
    results = ValidationResult.find_by_user(None)
    
    return jsonify({
        "success": True,
        "results": serialize_doc(results)
    }) 