from utils.db import get_db
from utils.auth import hash_password

db = get_db()
users = db.users

ADMIN_EMAIL = "Placementcell@cbscollege"
ADMIN_PASSWORD = "Placement123"

# remove existing admin
users.delete_many({'role': 'admin'})

# create new admin
users.insert_one({
    'email': ADMIN_EMAIL,
    'password': hash_password(ADMIN_PASSWORD),
    'role': 'admin'
})

print("Admin updated successfully")
print("Email:", ADMIN_EMAIL)
print("Password:", ADMIN_PASSWORD)
