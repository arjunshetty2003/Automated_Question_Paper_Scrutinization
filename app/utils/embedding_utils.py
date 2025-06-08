import google.generativeai as genai
import json

class Document:
    """Simple document class to mimic LangChain's Document class"""
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}

class GeminiEmbeddingProvider:
    def __init__(self, api_key=None):
        if api_key:
            genai.configure(api_key=api_key)
        self.model = "gemini-1.5-flash"
        
    def get_single_embedding(self, text, task_type="RETRIEVAL_QUERY"):
        """Get embedding for a single text string"""
        try:
            embed_model = genai.get_embeddings_model("models/embedding-001")
            result = embed_model.embed_content(
                content=text,
                task_type=task_type
            )
            return result.embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Return a zero vector of appropriate dimension as fallback
            return [0.0] * 768  # Typical embedding dimension
    
    def get_completion(self, prompt, max_tokens=1024):
        """Get text completion from Gemini"""
        try:
            completion_model = genai.GenerativeModel(self.model)
            response = completion_model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error getting completion: {e}")
            return f"ERROR_LLM_CALL: {str(e)}"
