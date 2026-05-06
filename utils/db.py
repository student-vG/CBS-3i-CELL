from pymongo import MongoClient
import gridfs
import os
from urllib.parse import quote_plus

# Get MONGO_URI from environment, or construct it from components
MONGO_URI = os.getenv('MONGO_URI', None)

# If MONGO_URI not set, try to build from components
if not MONGO_URI:
    mongo_user = os.getenv('MONGO_USER', 'placement_user')
    mongo_password = os.getenv('MONGO_PASSWORD', '')
    mongo_host = os.getenv('MONGO_HOST', 'localhost')
    mongo_port = os.getenv('MONGO_PORT', '27017')
    
    if mongo_password:
        # URL-encode password to handle special characters
        encoded_password = quote_plus(mongo_password)
        MONGO_URI = f'mongodb+srv://{mongo_user}:{encoded_password}@{mongo_host}/?retryWrites=true&w=majority'
    else:
        MONGO_URI = f'mongodb://{mongo_host}:{mongo_port}'

DB_NAME = 'placement_system'

def get_db():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db

def get_fs():
    db = get_db()
    return gridfs.GridFS(db)

