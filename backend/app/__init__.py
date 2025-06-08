import os
from flask import Flask
from flask_cors import CORS
from config import config
from .models.db_models import init_db
from bson import ObjectId
import json
from flask.json import JSONEncoder

class MongoJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Apply configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Setup CORS
    CORS(app)
    
    # Set custom JSON encoder
    app.json_encoder = MongoJSONEncoder
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    from .api.routes import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    return app 