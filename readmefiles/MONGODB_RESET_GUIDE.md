# MongoDB Fresh Start Guide

This guide provides step-by-step instructions to completely reset your MongoDB database and start fresh with all features implemented.

## Prerequisites

1. MongoDB installed locally or MongoDB Atlas account
2. Access to your MongoDB connection string
3. Python installed with the project dependencies

## Option 1: Reset Using MongoDB Compass (GUI)

### Step 1: Connect to MongoDB

1. Open MongoDB Compass
2. Enter your connection string (e.g., `mongodb://localhost:27017` or your Atlas URI)
3. Click "Connect"

### Step 2: Delete the Database

1. In the left sidebar, find your database (likely named `placement_cell` or `test`)
2. Click on the database name
3. Click "Drop Database" button
4. Confirm the deletion

### Step 3: Create Fresh Database

1. Click "Create Database" button
2. Enter database name: `placement_cell`
3. Enter collection name: `users` (first collection)
4. Click "Create Database"

### Step 4: Create Required Collections

Create the following collections:

- `users`
- `students`
- `jobs`
- `applications`
- `announcements`
- `experiences`
- `notifications`
- `login_logs`
- `forms`
- `form_responses`
- `password_requests`

## Option 2: Reset Using MongoDB Shell (CLI)

### Step 1: Open MongoDB Shell

```bash
# For local MongoDB
mongosh

# For MongoDB Atlas
mongosh "mongodb+srv://<your-connection-string>"
```

### Step 2: Drop Database

```javascript
// Show all databases
show dbs

// Switch to your database
use placement_cell

// Drop the entire database
db.dropDatabase()

// Exit
exit
```

### Step 3: Recreate Collections with Indexes

```javascript
use placement_cell

// Users collection
db.createCollection("users")
db.users.createIndex("email", { unique: true })

// Students collection
db.createCollection("students")
db.students.createIndex("user_id")
db.students.createIndex("student_id")

// Jobs collection
db.createCollection("jobs")
db.jobs.createIndex("status")
db.jobs.createIndex("created_at")
db.jobs.createIndex("expires_at")

// Applications collection
db.createCollection("applications")
db.applications.createIndex("student_id")
db.applications.createIndex("job_id")
db.applications.createIndex("status")

// Announcements collection
db.createCollection("announcements")
db.announcements.createIndex("status")
db.announcements.createIndex("created_at")

// Notifications collection
db.createCollection("notifications")
db.notifications.createIndex("user_id")
db.notifications.createIndex("is_read")

// Login logs collection
db.createCollection("login_logs")
db.login_logs.createIndex("user_id")
db.login_logs.createIndex("login_time")

// Forms collection
db.createCollection("forms")
db.forms.createIndex("is_active")

// Form responses collection
db.form_responses.createIndex("form_id")
db.form_responses.createIndex("student_id")

// Password requests collection
db.createCollection("password_requests")
db.password_requests.createIndex("email")
db.password_requests.createIndex("status")
```

## Option 3: Reset Using Python Script

Create a reset script:

```python
# reset_db.py
from pymongo import MongoClient
import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Or your Atlas URI
db = client["placement_cell"]

# List of collections to drop
collections = [
    'users', 'students', 'jobs', 'applications',
    'announcements', 'experiences', 'notifications',
    'login_logs', 'forms', 'form_responses', 'password_requests'
]

# Drop all collections
for coll in collections:
    if coll in db.list_collection_names():
        db[coll].drop()
        print(f"Dropped: {coll}")
    else:
        print(f"Skipped (not exists): {coll}")

# Create indexes
# Users
db.users.create_index("email", unique=True)

# Students
db.students.create_index("user_id")
db.students.create_index("student_id")

# Jobs
db.jobs.create_index("status")
db.jobs.create_index("created_at")
db.jobs.create_index("expires_at")

# Applications
db.applications.create_index("student_id")
db.applications.create_index("job_id")
db.applications.create_index("status")

# Announcements
db.announcements.create_index("status")
db.announcements.create_index("created_at")

# Notifications
db.notifications.create_index("user_id")
db.notifications.create_index("is_read")

# Login logs
db.login_logs.create_index("user_id")
db.login_logs.create_index("login_time")

# Forms
db.forms.create_index("is_active")

# Form responses
db.form_responses.create_index("form_id")
db.form_responses.create_index("student_id")

# Password requests
db.password_requests.create_index("email")
db.password_requests.create_index("status")

print("Database reset complete!")
print("\nNow create your admin user:")
print("1. Go to /signup")
print("2. Select 'Admin' role")
print("3. Enter admin details")
print("4. First admin will be Super Admin automatically")
```

Run the script:

```bash
python reset_db.py
```

## Step 4: Create Initial Admin User

### Method 1: Through Web Interface

1. Go to `http://localhost:5000/signup`
2. Select "Admin / Faculty" role
3. Enter your details
4. First admin registered becomes Super Admin automatically

### Method 2: Create Admin Directly (MongoDB Shell)

```javascript
use placement_cell

// Create admin user
db.users.insertOne({
    email: "admin@CBS.com",
    password: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.dW8KIuJ3eHFfOi", // "admin123" hashed
    role: "admin",
    admin_level: "super_admin",
    is_approved: true,
    approved_at: new Date(),
    approved_by: "system",
    full_name: "System Administrator",
    created_at: new Date()
})

// Verify
db.users.find({ role: "admin" }).pretty()
```

Default admin credentials:

- Email: `admin@CBS.com`
- Password: `admin123`

## Step 5: Verify Database Structure

Run this verification script:

```python
# verify_db.py
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["placement_cell"]

print("Database Collections:")
for coll in db.list_collection_names():
    count = db[coll].count_documents({})
    print(f"  - {coll}: {count} documents")

print("\nIndexes on users collection:")
for index in db.users.index_information():
    print(f"  - {index}")

print("\nSample admin user:")
admin = db.users.find_one({ "role": "admin" })
if admin:
    print(f"  Email: {admin['email']}")
    print(f"  Role: {admin['role']}")
    print(f"  Admin Level: {admin.get('admin_level', 'N/A')}")
else:
    print("  No admin users found")
```

## Common Issues & Solutions

### Issue: Authentication Failed

**Solution:**

1. Check your MongoDB connection string
2. For Atlas, ensure your IP is whitelisted
3. Verify username/password are correct

### Issue: Database Not Found

**Solution:**

1. The database will be created automatically on first write
2. Or create it manually in MongoDB Compass/Shell

### Issue: Index Creation Failed

**Solution:**

1. Drop the collection first
2. Then create indexes on empty collection
3. Or use `dropIndexes()` before recreating

### Issue: Connection Timeout

**Solution:**

1. Check MongoDB service is running
2. For Atlas, check network connectivity
3. Increase timeout in connection string: `mongodb://localhost:27017/?connectTimeoutMS=30000`

## Environment Variables

Create a `.env` file for MongoDB URI:

```env
MONGODB_URI=mongodb://localhost:27017/placement_cell
# Or for MongoDB Atlas:
# MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/placement_cell
```

## Features Now Active After Reset

After completing the reset, all these features are now working:

1. **Notification System**: Real-time polling for new notifications
2. **Student Form Data**: Show all filled forms after signup, Excel export
3. **Job Application Automation**: Auto-fill profile data during job apply
4. **Multiple Company Detection**: Red highlight for students applying to 2+ companies
5. **Interview/GD Attendance**: Student confirmation, notifications to admins
6. **Forgot Password (No SMTP)**: Super Admin approval flow
7. **Townhall Document Preview**: In-app document preview functionality
8. **Excel Exports**: Comprehensive exports matching dashboard data

## Need Help?

- MongoDB Documentation: https://docs.mongodb.com/
- MongoDB Compass Download: https://www.mongodb.com/products/compass
- MongoDB Atlas: https://www.mongodb.com/cloud/atlas
