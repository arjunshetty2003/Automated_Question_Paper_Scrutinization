import faiss
import numpy as np
import os
import pickle
from typing import Optional

class FAISSManager:
    """FAISS vector database operations manager."""
    
    @staticmethod
    def save_faiss_index(faiss_index_object, documents_metadata: list, filepath: str) -> bool:
        """Save FAISS index and associated metadata to disk."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(faiss_index_object, filepath)
            
            # Save metadata
            metadata_filepath = filepath.replace('.faiss', '_metadata.pkl')
            with open(metadata_filepath, 'wb') as f:
                pickle.dump(documents_metadata, f)
            
            return True
        except Exception as e:
            print(f"Error saving FAISS index: {e}")
            return False
    
    @staticmethod
    def load_faiss_index(filepath: str) -> Optional[tuple]:
        """Load FAISS index and metadata from disk."""
        try:
            if not os.path.exists(filepath):
                return None
            
            # Load FAISS index
            index = faiss.read_index(filepath)
            
            # Load metadata
            metadata_filepath = filepath.replace('.faiss', '_metadata.pkl')
            with open(metadata_filepath, 'rb') as f:
                metadata = pickle.load(f)
            
            return index, metadata
        except Exception as e:
            print(f"Error loading FAISS index: {e}")
            return None
    
    @staticmethod
    def create_faiss_index(embeddings: np.ndarray) -> faiss.Index:
        """Create a FAISS index from embeddings."""
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner product similarity
        index.add(embeddings.astype('float32'))
        return index
