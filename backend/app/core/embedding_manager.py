import google.generativeai as genai
from flask import current_app
import numpy as np
import faiss
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import os
from app.db.faiss_db import FAISSManager
from app.db.mongo_db import MongoDBManager

@dataclass
class SimpleDocument:
    """Simple document structure for embedding storage."""
    content: str
    metadata: Dict
    
class SimpleVectorStoreFAISS:
    """Simple FAISS vector store implementation."""
    
    def __init__(self, documents: List[SimpleDocument], embeddings_list: List[List[float]]):
        """
        Initialize FAISS vector store.
        
        Args:
            documents: List of SimpleDocument objects
            embeddings_list: List of embeddings corresponding to documents
        """
        self.documents = documents
        self.embeddings = np.array(embeddings_list, dtype='float32')
        
        # Create FAISS index
        dimension = self.embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner product similarity
        self.faiss_index.add(self.embeddings)
    
    def search(self, query_text: str, k: int = 5) -> List[Tuple[SimpleDocument, float]]:
        """
        Search for similar documents.
        
        Args:
            query_text: Query text to search for
            k: Number of top results to return
        
        Returns:
            List of tuples (document, similarity_score)
        """
        # Get query embedding
        query_embedding = get_gemini_embeddings([query_text])
        if not query_embedding:
            return []
        
        query_vector = np.array(query_embedding, dtype='float32')
        
        # Ensure k doesn't exceed available documents
        actual_k = min(k, self.faiss_index.ntotal)
        
        # Search
        similarities, indices = self.faiss_index.search(query_vector, actual_k)
        
        # Return results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx]
                score = float(similarities[0][i])
                results.append((doc, score))
        
        return results

def configure_gemini_embedding():
    """Configure Gemini API for embeddings."""
    api_key = current_app.config.get('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
    else:
        raise ValueError("GEMINI_API_KEY not found in configuration")

def get_gemini_embeddings(texts: List[str], batch_size: int = 10) -> List[List[float]]:
    """
    Get embeddings for a list of texts using Gemini API.
    
    Args:
        texts: List of texts to embed
        batch_size: Number of texts to process in each batch
    
    Returns:
        List of embeddings
    """
    configure_gemini_embedding()
    model_name = current_app.config.get('EMBEDDING_MODEL_NAME', 'models/embedding-001')
    
    all_embeddings = []
    
    # Process in batches
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            # Get embeddings for batch
            embeddings = genai.embed_content(
                model=model_name,
                content=batch,
                task_type="retrieval_document"
            )
            
            if hasattr(embeddings, 'embedding'):
                # Single text
                all_embeddings.append(embeddings['embedding'])
            else:
                # Multiple texts
                for embedding in embeddings['embedding']:
                    all_embeddings.append(embedding)
                    
        except Exception as e:
            print(f"Error getting embeddings for batch {i//batch_size + 1}: {e}")
            # Add zero embeddings for failed batch
            for _ in batch:
                all_embeddings.append([0.0] * 768)  # Default dimension
    
    return all_embeddings

def build_and_save_faiss_indexes_for_subject(
    subject_id: str, 
    syllabus_docs: List[SimpleDocument], 
    textbook_docs: List[SimpleDocument]
) -> bool:
    """
    Build and save FAISS indexes for a subject.
    
    Args:
        subject_id: Subject ID
        syllabus_docs: List of syllabus documents
        textbook_docs: List of textbook documents
    
    Returns:
        bool: True if successful
    """
    try:
        faiss_folder = current_app.config['FAISS_INDEX_FOLDER']
        subject_folder = os.path.join(faiss_folder, subject_id)
        os.makedirs(subject_folder, exist_ok=True)
        
        # Build syllabus index if documents exist
        if syllabus_docs:
            syllabus_texts = [doc.content for doc in syllabus_docs]
            syllabus_embeddings = get_gemini_embeddings(syllabus_texts)
            
            if syllabus_embeddings:
                syllabus_vector_store = SimpleVectorStoreFAISS(syllabus_docs, syllabus_embeddings)
                syllabus_path = os.path.join(subject_folder, 'syllabus.faiss')
                
                # Save to disk
                FAISSManager.save_faiss_index(
                    syllabus_vector_store.faiss_index,
                    [doc.metadata for doc in syllabus_docs],
                    syllabus_path
                )
                
                # Update MongoDB
                MongoDBManager.save_faiss_index_path(subject_id, 'syllabus', syllabus_path)
        
        # Build textbook index if documents exist
        if textbook_docs:
            textbook_texts = [doc.content for doc in textbook_docs]
            textbook_embeddings = get_gemini_embeddings(textbook_texts)
            
            if textbook_embeddings:
                textbook_vector_store = SimpleVectorStoreFAISS(textbook_docs, textbook_embeddings)
                textbook_path = os.path.join(subject_folder, 'textbook.faiss')
                
                # Save to disk
                FAISSManager.save_faiss_index(
                    textbook_vector_store.faiss_index,
                    [doc.metadata for doc in textbook_docs],
                    textbook_path
                )
                
                # Update MongoDB
                MongoDBManager.save_faiss_index_path(subject_id, 'textbook', textbook_path)
        
        return True
        
    except Exception as e:
        print(f"Error building FAISS indexes for subject {subject_id}: {e}")
        return False

def load_vector_store_for_subject(subject_id: str, index_type: str) -> Optional[SimpleVectorStoreFAISS]:
    """
    Load vector store for a subject.
    
    Args:
        subject_id: Subject ID
        index_type: Type of index ('syllabus' or 'textbook')
    
    Returns:
        SimpleVectorStoreFAISS object or None
    """
    try:
        # Get index path from MongoDB
        index_path = MongoDBManager.get_faiss_index_path(subject_id, index_type)
        if not index_path or not os.path.exists(index_path):
            return None
        
        # Load FAISS index and metadata
        result = FAISSManager.load_faiss_index(index_path)
        if not result:
            return None
        
        faiss_index, metadata_list = result
        
        # Reconstruct SimpleDocument objects
        documents = []
        for metadata in metadata_list:
            # Create dummy content - in practice, you might want to store content separately
            doc = SimpleDocument(content="", metadata=metadata)
            documents.append(doc)
        
        # Create vector store object
        vector_store = SimpleVectorStoreFAISS.__new__(SimpleVectorStoreFAISS)
        vector_store.documents = documents
        vector_store.faiss_index = faiss_index
        vector_store.embeddings = None  # Not needed for search
        
        return vector_store
        
    except Exception as e:
        print(f"Error loading vector store for subject {subject_id}, type {index_type}: {e}")
        return None
