import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MONGO_URI = os.environ.get('MONGO_DB_URI') or 'mongodb://localhost:27017/qp_scrutinization'
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'uploaded_files')
    FAISS_INDEX_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'faiss_indexes')
    
    # Gemini API settings
    EMBEDDING_MODEL_NAME = "models/embedding-001"
    GENERATIVE_MODEL_NAME = "gemini-1.5-flash"

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = 'production'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
