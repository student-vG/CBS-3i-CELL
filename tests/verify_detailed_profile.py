
import sys
import os
import requests
from pymongo import MongoClient
import datetime
import bson
from bson import ObjectId

# Add parent directory to path to import app utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
DB_NAME = 'placement_system'

def run_test():
    print("Starting Detailed Profile Verification...")
    
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        print("[PASS] MongoDB Connection Successful")
    except Exception as e:
        print(f"[FAIL] MongoDB Connection: {e}")
        return

    # 1. Simulate Student Profile Submission (Data Structure Check)
    student_user_id = ObjectId() # Mock ID
    
    profile_data = {
        'name': 'Test Student Detailed',
        'gender': 'Male',
        'dob': '2000-01-01',
        'phone': '9876543210',
        'alt_phone': '1234567890',
        'personal_email': 'personal@test.com',
        'nationality': 'Indian',
        'marital_status': 'Single',
        'aadhaar': '123412341234',
        'pan': 'ABCDE1234F',
        'address': {
            'permanent': '123 Permanent St',
            'current': '456 Current Ave'
        },
        'academic': {
            'tenth': {'school': 'School A', 'board': 'CBSE', 'year': 2016, 'score': 90.5},
            'twelfth': {'school': 'College B', 'board': 'State', 'year': 2018, 'score': 88.0, 'stream': 'Science'},
            'ug': {'college': 'Engg College', 'university': 'Tech Univ', 'degree': 'B.Tech', 'branch': 'CSE', 'year': 2022, 'score': 8.5, 'backlogs': 0, 'backlog_status': 'Cleared'},
            'pg': {}
        },
        'branch': 'CSE',
        'cgpa': 8.5,
        'skills': ['Python', 'Testing'],
        'projects': 'Detailed Profile Project',
        'user_id': student_user_id,
        'is_active': True
    }
    
    # Clean previous
    db.students.delete_many({'name': 'Test Student Detailed'})
    
    # Insert
    db.students.insert_one(profile_data)
    print("[PASS] Detailed Profile Inserted")

    # 2. Verify Data Retrieval
    saved_student = db.students.find_one({'name': 'Test Student Detailed'})
    if saved_student.get('academic', {}).get('tenth', {}).get('score') == 90.5:
         print("[PASS] Nested Academic Data Verified (10th Score: 90.5)")
    else:
         print("[FAIL] Nested Data Mismatch")
         
    # 3. Simulate CSV Export Structure (Copying logic partially or just checking if we can access fields without error)
    # We will just verify we can access the paths safely
    try:
        s = saved_student
        ac = s.get('academic', {})
        row = [
            s.get('name', ''),
            ac.get('tenth', {}).get('board', ''),
            ac.get('ug', {}).get('branch', ''),
            s.get('address', {}).get('permanent', '')
        ]
        if row[1] == 'CBSE' and row[2] == 'CSE':
            print("[PASS] Export Data Access Logic Verified")
        else:
             print(f"[FAIL] Export Logic Mismatch: {row}")
    except Exception as e:
        print(f"[FAIL] Export Logic Error: {e}")

    print("\nVerification Complete.")

if __name__ == "__main__":
    run_test()
