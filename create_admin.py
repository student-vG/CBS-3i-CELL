from utils.db import get_db
from utils.auth import hash_password
import datetime

db = get_db()
users = db.users

ADMIN_EMAIL = "Placementcell@cbscollege"
ADMIN_PASSWORD = "Placement123"

# Check if admin exists
existing_admin = users.find_one({'email': ADMIN_EMAIL})

if existing_admin:
    print("Admin already exists!")
else:
    # Create super admin
    users.insert_one({
        'email': ADMIN_EMAIL,
        'password': hash_password(ADMIN_PASSWORD),
        'role': 'admin',
        'admin_level': 'super_admin',
        'is_approved': True,
        'created_at': datetime.datetime.now()
    })
    print("✓ Super Admin created successfully!")

print("\nAdmin Credentials:")
print(f"Email: {ADMIN_EMAIL}")
print(f"Password: {ADMIN_PASSWORD}")
print(f"Role: Super Admin")
