import os
import json
import time
from flask import current_app
from ..utils.pdf_utils import load_syllabus_from_json, prepare_textbook_documents, SimpleDocument
from ..utils.embedding_utils import GeminiEmbeddingProvider
from ..utils.simple_vector_store import SimpleVectorStoreFAISS
from ..models.db_models import Syllabus, Textbook

def create_syllabus_vector_store(syllabus_id, file_path, user_id):
    """Create a vector store from a syllabus JSON file"""
    # Load syllabus from JSON
    documents, syllabus_data = load_syllabus_from_json(file_path)
    
    if not documents or not syllabus_data:
        return False, "Failed to load syllabus from JSON file"
    
    # Configure Gemini API
    gemini_provider = GeminiEmbeddingProvider(api_key=current_app.config.get('GEMINI_API_KEY'))
    
    # Get embeddings for documents
    texts = [doc.page_content for doc in documents]
    embeddings = gemini_provider.get_embeddings(texts)
    
    if not embeddings:
        return False, "Failed to get embeddings for syllabus"
    
    # Create vector store
    vector_store = SimpleVectorStoreFAISS(documents, embeddings)
    
    # Save vector store to disk
    save_path = os.path.join(
        current_app.config.get('FAISS_INDEX_DIR'),
        f"syllabus_{syllabus_id}"
    )
    
    if vector_store.save(save_path):
        # Update syllabus record in DB
        Syllabus.update_vectorized_status(syllabus_id, vectorized=True)
        return True, f"Syllabus vector store saved to {save_path}"
    else:
        return False, "Failed to save syllabus vector store"

def create_textbook_vector_store(textbook_id, file_path, user_id):
    """Create a vector store from a textbook PDF file"""
    # Process textbook PDF
    documents = prepare_textbook_documents(file_path)
    
    if not documents:
        return False, "Failed to extract text from textbook PDF"
    
    # Configure Gemini API
    gemini_provider = GeminiEmbeddingProvider(api_key=current_app.config.get('GEMINI_API_KEY'))
    
    # Get embeddings for documents
    texts = [doc.page_content for doc in documents]
    embeddings = gemini_provider.get_embeddings(texts)
    
    if not embeddings:
        return False, "Failed to get embeddings for textbook"
    
    # Create vector store
    vector_store = SimpleVectorStoreFAISS(documents, embeddings)
    
    # Save vector store to disk
    save_path = os.path.join(
        current_app.config.get('FAISS_INDEX_DIR'),
        f"textbook_{textbook_id}"
    )
    
    if vector_store.save(save_path):
        # Update textbook record in DB
        Textbook.update_vectorized_status(textbook_id, vectorized=True)
        return True, f"Textbook vector store saved to {save_path}"
    else:
        return False, "Failed to save textbook vector store"

def get_vector_store_path(resource_type, resource_id):
    """Get the path to a vector store file"""
    return os.path.join(
        current_app.config.get('FAISS_INDEX_DIR'),
        f"{resource_type}_{resource_id}"
    )

def check_vector_store_exists(resource_type, resource_id):
    """Check if a vector store exists for a resource"""
    base_path = get_vector_store_path(resource_type, resource_id)
    
    # Check if all necessary files exist
    index_file = f"{base_path}.index"
    documents_file = f"{base_path}.documents"
    meta_file = f"{base_path}.meta"
    vectors_file = f"{base_path}.vectors"
    
    return (
        os.path.exists(index_file) and
        os.path.exists(documents_file) and
        os.path.exists(meta_file) and
        os.path.exists(vectors_file)
    ) 