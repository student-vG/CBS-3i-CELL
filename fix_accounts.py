"""
Fix admin account and create missing user accounts.
"""
from utils.db import get_db
from utils.auth import hash_password
import datetime

db = get_db()
users = db.users
students = db.students

# ========================================
# FIX 1: Fix Admin Account
# ========================================
print("=" * 50)
print("FIX 1: Fixing Admin Account")
result = users.update_one(
    {'email': 'Placementcell@cbscollege'},
    {'$set': {
        'admin_level': 'super_admin',
        'is_approved': True,
        'name': 'Super Admin',
        'full_name': 'Super Admin'
    }}
)
print(f"  Admin 'Placementcell@cbscollege' fixed. Modified: {result.modified_count}")

# Also verify password works
admin = users.find_one({'email': 'Placementcell@cbscollege'})
if admin:
    from utils.auth import verify_password
    pwd_ok = verify_password(admin['password'], 'Placement123')
    print(f"  Password verification: {'OK' if pwd_ok else 'FAILED - will reset'}")
    if not pwd_ok:
        users.update_one(
            {'email': 'Placementcell@cbscollege'},
            {'$set': {'password': hash_password('Placement123')}}
        )
        print("  Password reset to 'Placement123'")

# ========================================
# FIX 2: Create Student 1 - bibiayesha@gmail.com
# ========================================
print("\n" + "=" * 50)
print("FIX 2: Creating Student - bibiayesha@gmail.com")
if not users.find_one({'email': 'bibiayesha@gmail.com'}):
    import random
    sid1 = f"CBS{datetime.datetime.now().year}{random.randint(1000,9999)}"
    uid1 = users.insert_one({
        'email': 'bibiayesha@gmail.com',
        'password': hash_password('ayesha1234'),
        'role': 'student',
        'is_approved': True,
        'profile_completed': True,
        'name': 'Bibi Ayesha',
        'created_at': datetime.datetime.now()
    }).inserted_id
    students.insert_one({
        'user_id': uid1,
        'student_id': sid1,
        'name': 'Bibi Ayesha',
        'registered_at': datetime.datetime.now(),
        'is_active': True,
        'cgpa': 8.0,
        'branch': 'MBA',
        'phone': '',
        'skills': [],
        'projects': ''
    })
    print(f"  Created student bibiayesha@gmail.com (ID: {sid1})")
else:
    print("  Student bibiayesha@gmail.com already exists")

# ========================================
# FIX 3: Create Student 2 - vikramgudihal@gmail.com
# ========================================
print("\n" + "=" * 50)
print("FIX 3: Creating Student - vikramgudihal@gmail.com")
if not users.find_one({'email': 'vikramgudihal@gmail.com'}):
    import random
    sid2 = f"CBS{datetime.datetime.now().year}{random.randint(1000,9999)}"
    uid2 = users.insert_one({
        'email': 'vikramgudihal@gmail.com',
        'password': hash_password('vg123'),
        'role': 'student',
        'is_approved': True,
        'profile_completed': True,
        'name': 'Vikram Gudihal',
        'created_at': datetime.datetime.now()
    }).inserted_id
    students.insert_one({
        'user_id': uid2,
        'student_id': sid2,
        'name': 'Vikram Gudihal',
        'registered_at': datetime.datetime.now(),
        'is_active': True,
        'cgpa': 7.5,
        'branch': 'MBA',
        'phone': '',
        'skills': [],
        'projects': ''
    })
    print(f"  Created student vikramgudihal@gmail.com (ID: {sid2})")
else:
    print("  Student vikramgudihal@gmail.com already exists")

# ========================================
# FIX 4: Create Faculty - sneha123@gmail.com
# ========================================
print("\n" + "=" * 50)
print("FIX 4: Creating Faculty - sneha123@gmail.com")
if not users.find_one({'email': 'sneha123@gmail.com'}):
    uid3 = users.insert_one({
        'email': 'sneha123@gmail.com',
        'password': hash_password('sneha123'),
        'role': 'admin',
        'admin_level': 'faculty',
        'is_approved': True,
        'full_name': 'Sneha',
        'name': 'Sneha',
        'created_at': datetime.datetime.now()
    }).inserted_id
    print(f"  Created faculty sneha123@gmail.com")
else:
    print("  Faculty sneha123@gmail.com already exists")

# ========================================
# SUMMARY
# ========================================
print("\n" + "=" * 50)
print("ALL ACCOUNTS SUMMARY:")
print("=" * 50)
for u in users.find({}, {'email': 1, 'role': 1, 'admin_level': 1, 'is_approved': 1, 'profile_completed': 1}):
    print(f"  {u['email']:35s} | role={str(u.get('role')):10s} | level={str(u.get('admin_level')):12s} | approved={str(u.get('is_approved')):5s} | profile={str(u.get('profile_completed'))}")

print("\n✅ All fixes applied successfully!")
print("\nLogin Credentials:")
print("  Super Admin: Placementcell@cbscollege / Placement123  (select 'Admin/Faculty')")
print("  Faculty:     sneha123@gmail.com / sneha123             (select 'Admin/Faculty')")
print("  Student 1:   bibiayesha@gmail.com / ayesha1234         (select 'Student')")
print("  Student 2:   vikramgudihal@gmail.com / vg123           (select 'Student')")
