import numpy as np
import pickle
import os

def cosine_similarity(a, b):
    """Compute cosine similarity between vectors a and b"""
    a_norm = np.linalg.norm(a, axis=1)
    b_norm = np.linalg.norm(b, axis=1)
    
    # Reshape a_norm to column vector and b_norm to row vector
    a_norm = a_norm.reshape(-1, 1)
    b_norm = b_norm.reshape(1, -1)
    
    # Compute dot product
    dot_product = np.dot(a, b.T)
    
    # Compute similarity
    similarity = dot_product / (np.dot(a_norm, b_norm) + 1e-8)
    
    return similarity

class SimpleVectorStoreFAISS:
    """A simple vector store implementation using numpy instead of FAISS"""
    
    def __init__(self, documents=None, vectors=None, load_from_path=None):
        self.vectors = []
        self.documents = []
        self.faiss_index = None  # For compatibility with existing code
        
        if load_from_path:
            self.load(load_from_path)
        elif documents is not None and vectors is not None:
            self.add_vectors(vectors, documents)
    
    def add_vectors(self, vectors, documents):
        """Add vectors and their corresponding documents to the store"""
        if not vectors or not documents:
            return
            
        if len(vectors) != len(documents):
            raise ValueError("Number of vectors and documents must match")
            
        self.vectors.extend(vectors)
        self.documents.extend(documents)
        
        # Set this for compatibility with the existing code that checks faiss_index.ntotal
        self.faiss_index = type('obj', (object,), {'ntotal': len(self.vectors)})
    
    def search(self, query, k=5, embedding_fn=None):
        """Search for the k most similar vectors to the query"""
        if not self.vectors:
            return []
            
        # Apply embedding function if provided
        if embedding_fn and isinstance(query, str):
            query_vector = embedding_fn(query)
        elif not isinstance(query, (list, np.ndarray)):
            raise ValueError("Query must be a vector or a string with an embedding function")
        else:
            query_vector = query
            
        query_vector = np.array(query_vector).reshape(1, -1)
        vectors_array = np.array(self.vectors)
        
        # Compute cosine similarities
        similarities = cosine_similarity(query_vector, vectors_array)[0]
        
        # Sort by similarity (descending) and get top k
        indices = np.argsort(similarities)[::-1][:k]
        
        # Format results to match the expected output format
        results = []
        for i, idx in enumerate(indices):
            distance = 1.0 - similarities[idx]  # Convert similarity to distance (1 - cosine_similarity)
            results.append({
                "document": self.documents[idx],
                "distance": float(distance)
            })
            
        return results
    
    def save(self, path):
        """Save the vector store to disk"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save index file (dummy for compatibility)
        with open(f"{path}.index", "wb") as f:
            pickle.dump({"ntotal": len(self.vectors)}, f)
            
        # Save documents
        with open(f"{path}.documents", "wb") as f:
            pickle.dump(self.documents, f)
            
        # Save metadata
        with open(f"{path}.meta", "wb") as f:
            pickle.dump({"version": "1.0"}, f)
            
        # Save vectors
        with open(f"{path}.vectors", "wb") as f:
            pickle.dump(self.vectors, f)
            
        return True
    
    def load(self, path):
        """Load the vector store from disk"""
        # Load vectors
        with open(f"{path}.vectors", "rb") as f:
            self.vectors = pickle.load(f)
            
        # Load documents
        with open(f"{path}.documents", "rb") as f:
            self.documents = pickle.load(f)
            
        # Set faiss_index for compatibility
        self.faiss_index = type('obj', (object,), {'ntotal': len(self.vectors)})
        
        return True
