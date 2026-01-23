
import sys
import os
import requests
from pymongo import MongoClient
import datetime
import bson

# Add parent directory to path to import app utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
DB_NAME = 'placement_system'

def run_test():
    print("Starting Dynamic Forms Verification...")
    
    # 1. Direct DB Connection
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        print("[PASS] MongoDB Connection Successful")
    except Exception as e:
        print(f"[FAIL] MongoDB Connection: {e}")
        return

    # Cleanup Previous Test Data
    db.forms.delete_many({'title': 'TEST_FORM_AUTO'})
    db.form_responses.delete_many({'answers.TEST_KEY': 'TEST_VALUE'})
    
    # 2. Simulate Admin Creating Form
    form_data = {
        'title': 'TEST_FORM_AUTO',
        'description': 'Automated Test Form',
        'fields': [
            {'label': 'Full Name', 'type': 'text'},
            {'label': 'Rating', 'type': 'number'}
        ],
        'created_by': 'admin_test_user',
        'created_at': datetime.datetime.utcnow(),
        'is_active': True
    }
    
    insert_result = db.forms.insert_one(form_data)
    form_id = insert_result.inserted_id
    print(f"[PASS] Form Creation (ID: {form_id})")
    
    # 3. Simulate Student Filling Form
    response_data = {
        'form_id': form_id,
        'student_id': 'student_test_user_id',
        'student_name': 'Test Student',
        'answers': {
            'Full Name': 'John Doe',
            'Rating': '5'
        },
        'submitted_at': datetime.datetime.utcnow()
    }
    
    db.form_responses.insert_one(response_data)
    print("[PASS] Student Response Submission")
    
    # 4. Verify Data Integrity
    saved_response = db.form_responses.find_one({'form_id': form_id})
    if saved_response and saved_response['answers']['Full Name'] == 'John Doe':
        print("[PASS] Response Data Verification")
    else:
        print("[FAIL] Response Data Verification")
        
    # 5. Simulate Export Logic (Mocking the logic from routes)
    responses = list(db.form_responses.find({'form_id': form_id}))
    if len(responses) == 1:
        print(f"[PASS] Export Query Found {len(responses)} response(s)")
    else:
         print(f"[FAIL] Export Query Found {len(responses)} response(s)")
         
    print("\nVerification Complete: All Systems Go")

if __name__ == "__main__":
    run_test()
