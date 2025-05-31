from app import mongo
from bson import ObjectId
from bson.errors import InvalidId
from typing import List, Dict, Optional
import datetime

class MongoDBManager:
    """MongoDB operations manager for the application."""
    
    @staticmethod
    def get_subjects_collection():
        """Get subjects collection."""
        return mongo.db.subjects
    
    @staticmethod
    def get_users_collection():
        """Get users collection."""
        return mongo.db.users
    
    # Subject operations
    @staticmethod
    def add_subject(name: str) -> str:
        """Add a new subject and return its ID."""
        subject_data = {
            'name': name,
            'created_at': datetime.datetime.utcnow(),
            'syllabus': None,
            'textbooks': [],
            'faiss_indexes': {}
        }
        result = MongoDBManager.get_subjects_collection().insert_one(subject_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_subject_by_id(subject_id: str) -> Optional[Dict]:
        """Get subject by ID."""
        try:
            obj_id = ObjectId(subject_id)
            subject = MongoDBManager.get_subjects_collection().find_one({'_id': obj_id})
            if subject:
                subject['_id'] = str(subject['_id'])
            return subject
        except InvalidId:
            return None
    
    @staticmethod
    def get_subject_by_name(name: str) -> Optional[Dict]:
        """Get subject by name."""
        subject = MongoDBManager.get_subjects_collection().find_one({'name': name})
        if subject:
            subject['_id'] = str(subject['_id'])
        return subject
    
    @staticmethod
    def list_subjects() -> List[Dict]:
        """List all subjects."""
        subjects = list(MongoDBManager.get_subjects_collection().find())
        for subject in subjects:
            subject['_id'] = str(subject['_id'])
        return subjects
    
    @staticmethod
    def update_subject_syllabus(subject_id: str, syllabus_json: Dict) -> bool:
        """Update subject syllabus."""
        try:
            obj_id = ObjectId(subject_id)
            result = MongoDBManager.get_subjects_collection().update_one(
                {'_id': obj_id},
                {
                    '$set': {
                        'syllabus': syllabus_json,
                        'updated_at': datetime.datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except InvalidId:
            return False
    
    @staticmethod
    def get_syllabus_for_subject(subject_id: str) -> Optional[Dict]:
        """Get syllabus for a subject."""
        subject = MongoDBManager.get_subject_by_id(subject_id)
        return subject['syllabus'] if subject else None
    
    @staticmethod
    def add_textbook_to_subject(subject_id: str, filename: str, stored_filepath: str, original_filename: str) -> bool:
        """Add textbook metadata to subject."""
        try:
            obj_id = ObjectId(subject_id)
            textbook_data = {
                'filename': filename,
                'stored_filepath': stored_filepath,
                'original_filename': original_filename,
                'uploaded_at': datetime.datetime.utcnow()
            }
            result = MongoDBManager.get_subjects_collection().update_one(
                {'_id': obj_id},
                {
                    '$push': {'textbooks': textbook_data},
                    '$set': {'updated_at': datetime.datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except InvalidId:
            return False
    
    @staticmethod
    def get_textbooks_for_subject(subject_id: str) -> List[Dict]:
        """Get textbooks for a subject."""
        subject = MongoDBManager.get_subject_by_id(subject_id)
        return subject['textbooks'] if subject else []
    
    @staticmethod
    def delete_subject_data(subject_id: str) -> bool:
        """Delete subject and all associated data."""
        try:
            obj_id = ObjectId(subject_id)
            result = MongoDBManager.get_subjects_collection().delete_one({'_id': obj_id})
            return result.deleted_count > 0
        except InvalidId:
            return False
    
    @staticmethod
    def save_faiss_index_path(subject_id: str, index_type: str, path: str) -> bool:
        """Save FAISS index path for a subject."""
        try:
            obj_id = ObjectId(subject_id)
            result = MongoDBManager.get_subjects_collection().update_one(
                {'_id': obj_id},
                {
                    '$set': {
                        f'faiss_indexes.{index_type}': path,
                        'updated_at': datetime.datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except InvalidId:
            return False
    
    @staticmethod
    def get_faiss_index_path(subject_id: str, index_type: str) -> Optional[str]:
        """Get FAISS index path for a subject."""
        subject = MongoDBManager.get_subject_by_id(subject_id)
        if subject and 'faiss_indexes' in subject:
            return subject['faiss_indexes'].get(index_type)
        return None
    
    # User operations
    @staticmethod
    def create_user(username: str, hashed_password: str, role: str) -> str:
        """Create a new user."""
        user_data = {
            'username': username,
            'password': hashed_password,
            'role': role,
            'created_at': datetime.datetime.utcnow(),
            'is_active': True
        }
        result = MongoDBManager.get_users_collection().insert_one(user_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict]:
        """Get user by username."""
        user = MongoDBManager.get_users_collection().find_one({'username': username})
        if user:
            user['_id'] = str(user['_id'])
        return user
