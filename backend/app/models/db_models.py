import datetime
from pymongo import MongoClient
from flask import current_app
from bson import ObjectId

# MongoDB connection
client = None
db = None

def init_db(app):
    global client, db
    client = MongoClient(app.config['MONGO_URI'])
    db = client.get_default_database()
    
    # Create indexes for faster queries
    db.users.create_index('email', unique=True)
    db.syllabus.create_index('user_id')
    db.textbooks.create_index('user_id')
    db.question_papers.create_index('user_id')
    db.results.create_index('user_id')

# User model
class User:
    collection = 'users'
    
    @staticmethod
    def create(email, password_hash, name=None, role='user'):
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'name': name,
            'role': role,
            'created_at': datetime.datetime.utcnow(),
            'updated_at': datetime.datetime.utcnow()
        }
        result = db[User.collection].insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return user_data
    
    @staticmethod
    def find_by_email(email):
        return db[User.collection].find_one({'email': email})
    
    @staticmethod
    def find_by_id(user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        return db[User.collection].find_one({'_id': user_id})

# Syllabus model
class Syllabus:
    collection = 'syllabus'
    
    @staticmethod
    def create(user_id, name, file_path, course_name, units, vectorized=False):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        syllabus_data = {
            'user_id': user_id,
            'name': name,
            'file_path': file_path,
            'course_name': course_name,
            'units': units,
            'vectorized': vectorized,
            'created_at': datetime.datetime.utcnow(),
            'updated_at': datetime.datetime.utcnow()
        }
        result = db[Syllabus.collection].insert_one(syllabus_data)
        syllabus_data['_id'] = result.inserted_id
        return syllabus_data
    
    @staticmethod
    def find_by_id(syllabus_id):
        if isinstance(syllabus_id, str):
            syllabus_id = ObjectId(syllabus_id)
        return db[Syllabus.collection].find_one({'_id': syllabus_id})
    
    @staticmethod
    def find_by_user(user_id, limit=10, skip=0):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        cursor = db[Syllabus.collection].find({'user_id': user_id}).sort('created_at', -1).skip(skip).limit(limit)
        return list(cursor)
    
    @staticmethod
    def update_vectorized_status(syllabus_id, vectorized=True):
        if isinstance(syllabus_id, str):
            syllabus_id = ObjectId(syllabus_id)
        db[Syllabus.collection].update_one(
            {'_id': syllabus_id},
            {'$set': {'vectorized': vectorized, 'updated_at': datetime.datetime.utcnow()}}
        )

# Textbook model
class Textbook:
    collection = 'textbooks'
    
    @staticmethod
    def create(user_id, name, file_path, syllabus_id=None, vectorized=False):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        if syllabus_id and isinstance(syllabus_id, str):
            syllabus_id = ObjectId(syllabus_id)
        
        textbook_data = {
            'user_id': user_id,
            'name': name,
            'file_path': file_path,
            'syllabus_id': syllabus_id,
            'vectorized': vectorized,
            'created_at': datetime.datetime.utcnow(),
            'updated_at': datetime.datetime.utcnow()
        }
        result = db[Textbook.collection].insert_one(textbook_data)
        textbook_data['_id'] = result.inserted_id
        return textbook_data
    
    @staticmethod
    def find_by_id(textbook_id):
        if isinstance(textbook_id, str):
            textbook_id = ObjectId(textbook_id)
        return db[Textbook.collection].find_one({'_id': textbook_id})
    
    @staticmethod
    def find_by_user(user_id, limit=10, skip=0):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        cursor = db[Textbook.collection].find({'user_id': user_id}).sort('created_at', -1).skip(skip).limit(limit)
        return list(cursor)
    
    @staticmethod
    def find_by_syllabus(syllabus_id):
        if isinstance(syllabus_id, str):
            syllabus_id = ObjectId(syllabus_id)
        return list(db[Textbook.collection].find({'syllabus_id': syllabus_id}))
    
    @staticmethod
    def update_vectorized_status(textbook_id, vectorized=True):
        if isinstance(textbook_id, str):
            textbook_id = ObjectId(textbook_id)
        db[Textbook.collection].update_one(
            {'_id': textbook_id},
            {'$set': {'vectorized': vectorized, 'updated_at': datetime.datetime.utcnow()}}
        )

# Question Paper model
class QuestionPaper:
    collection = 'question_papers'
    
    @staticmethod
    def create(user_id, name, file_path, syllabus_id=None, questions=None):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        if syllabus_id and isinstance(syllabus_id, str):
            syllabus_id = ObjectId(syllabus_id)
        
        question_paper_data = {
            'user_id': user_id,
            'name': name,
            'file_path': file_path,
            'syllabus_id': syllabus_id,
            'questions': questions or [],
            'created_at': datetime.datetime.utcnow(),
            'updated_at': datetime.datetime.utcnow()
        }
        result = db[QuestionPaper.collection].insert_one(question_paper_data)
        question_paper_data['_id'] = result.inserted_id
        return question_paper_data
    
    @staticmethod
    def find_by_id(question_paper_id):
        if isinstance(question_paper_id, str):
            question_paper_id = ObjectId(question_paper_id)
        return db[QuestionPaper.collection].find_one({'_id': question_paper_id})
    
    @staticmethod
    def find_by_user(user_id, limit=10, skip=0):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        cursor = db[QuestionPaper.collection].find({'user_id': user_id}).sort('created_at', -1).skip(skip).limit(limit)
        return list(cursor)

# Result model for storing validation results
class ValidationResult:
    collection = 'results'
    
    @staticmethod
    def create(user_id, question_paper_id, syllabus_id, textbook_ids, validation_summary, errors=None):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        if isinstance(question_paper_id, str):
            question_paper_id = ObjectId(question_paper_id)
        
        if isinstance(syllabus_id, str):
            syllabus_id = ObjectId(syllabus_id)
            
        if textbook_ids:
            textbook_ids = [ObjectId(id) if isinstance(id, str) else id for id in textbook_ids]
            
        result_data = {
            'user_id': user_id,
            'question_paper_id': question_paper_id,
            'syllabus_id': syllabus_id,
            'textbook_ids': textbook_ids,
            'validation_summary': validation_summary,
            'errors': errors or [],
            'created_at': datetime.datetime.utcnow()
        }
        result = db[ValidationResult.collection].insert_one(result_data)
        result_data['_id'] = result.inserted_id
        return result_data
    
    @staticmethod
    def find_by_id(result_id):
        if isinstance(result_id, str):
            result_id = ObjectId(result_id)
        return db[ValidationResult.collection].find_one({'_id': result_id})
    
    @staticmethod
    def find_by_user(user_id, limit=10, skip=0):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        cursor = db[ValidationResult.collection].find({'user_id': user_id}).sort('created_at', -1).skip(skip).limit(limit)
        return list(cursor)
    
    @staticmethod
    def find_by_question_paper(question_paper_id):
        if isinstance(question_paper_id, str):
            question_paper_id = ObjectId(question_paper_id)
        return db[ValidationResult.collection].find_one({'question_paper_id': question_paper_id}) 