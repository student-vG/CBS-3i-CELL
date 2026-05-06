from pymongo import MongoClient
import os

# Read from environment variable (never hardcode passwords!)
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')

try:
    client = MongoClient(MONGO_URI)
    db = client['placement_system']
    print("✅ Connection Successful!")
    print("Databases:", client.list_database_names())
except Exception as e:
    print(f"❌ Connection Failed: {e}")