import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
    
    # MongoDB configuration
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/question_paper_scrutiny')
    
    # Google Gemini AI configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    EMBEDDING_MODEL_NAME = "models/text-embedding-004"
    GENERATIVE_MODEL_NAME = "gemini-1.5-flash-latest"
    
    # FAISS index path for persistence
    FAISS_INDEX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'faiss_indexes')
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 24  # 24 hours
    
    # Other settings
    LLM_CALL_DELAY_SECONDS = 2  # Delay between LLM calls for rate limiting
    
    @staticmethod
    def init_app(app):
        # Create upload and FAISS index directories if they don't exist
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.FAISS_INDEX_DIR, exist_ok=True)
        
        # Subdirectories for different file types
        os.makedirs(os.path.join(Config.UPLOAD_FOLDER, 'syllabus'), exist_ok=True)
        os.makedirs(os.path.join(Config.UPLOAD_FOLDER, 'textbooks'), exist_ok=True)
        os.makedirs(os.path.join(Config.UPLOAD_FOLDER, 'question_papers'), exist_ok=True)
        os.makedirs(os.path.join(Config.UPLOAD_FOLDER, 'results'), exist_ok=True)


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    # In production, ensure proper secret keys are set via environment variables
    

class TestingConfig(Config):
    TESTING = True
    # Use separate database for testing
    MONGO_URI = os.environ.get('TEST_MONGO_URI', 'mongodb://localhost:27017/question_paper_scrutiny_test')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 