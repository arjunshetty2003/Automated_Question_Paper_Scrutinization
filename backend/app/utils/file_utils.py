import os
import uuid
import re
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import shutil

def save_uploaded_file(file_storage: FileStorage, subject_id: str, file_type: str, base_upload_folder: str) -> str:
    """
    Save an uploaded file to a persistent directory.
    
    Args:
        file_storage: Flask FileStorage object
        subject_id: ID of the subject
        file_type: Type of file ('textbooks', 'question_papers')
        base_upload_folder: Base directory for uploads
    
    Returns:
        str: Path to the saved file
    """
    # Create directory structure
    subject_folder = os.path.join(base_upload_folder, file_type, subject_id)
    os.makedirs(subject_folder, exist_ok=True)
    
    # Generate unique filename
    original_filename = secure_filename(file_storage.filename)
    name, ext = os.path.splitext(original_filename)
    unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
    
    # Save file
    file_path = os.path.join(subject_folder, unique_filename)
    file_storage.save(file_path)
    
    return file_path

def delete_subject_files(subject_id: str, base_upload_folder: str) -> bool:
    """
    Delete all files associated with a subject.
    
    Args:
        subject_id: ID of the subject
        base_upload_folder: Base directory for uploads
    
    Returns:
        bool: True if successful
    """
    try:
        # Delete textbooks
        textbooks_folder = os.path.join(base_upload_folder, 'textbooks', subject_id)
        if os.path.exists(textbooks_folder):
            shutil.rmtree(textbooks_folder)
        
        # Delete question papers
        qp_folder = os.path.join(base_upload_folder, 'question_papers', subject_id)
        if os.path.exists(qp_folder):
            shutil.rmtree(qp_folder)
        
        return True
    except Exception as e:
        print(f"Error deleting subject files: {e}")
        return False

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """
    Check if file has an allowed extension.
    
    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions
    
    Returns:
        bool: True if file is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB."""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove or replace unsafe characters
    filename = re.sub(r'[^\w\s-.]', '', filename)
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename.strip('-')
