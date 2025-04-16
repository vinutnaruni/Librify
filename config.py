import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-secret-key'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/library_db'
    DEBUG = os.environ.get('DEBUG', 'True').lower() in ['true', '1', 'yes']
