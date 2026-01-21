from pymongo import MongoClient
import os

# Default to localhost if not specified
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
DB_NAME = 'placement_system'

def get_db():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db

