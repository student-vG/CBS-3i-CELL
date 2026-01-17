from flask import Flask, render_template, redirect, url_for, session, request, flash
from utils.db import get_db
from utils.auth import hash_password, verify_password, login_required
import os
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
import datetime
import csv
from io import StringIO
from flask import make_response

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Config
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize DB
db = get_db()
users_collection = db['users']
students_collection = db['students']
jobs_collection = db['jobs']
applications_collection = db['applications']
announcements_collection = db['announcements']
experiences_collection = db['experiences']
notifications_collection = db['notifications']

# Ensure unique index on email
users_collection.create_index("email", unique=True)

# --- ROUTES ---

@app.route('/')
def home():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('student_dashboard'))
    return render_template('login.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    
    user = users_collection.find_one({'email': email})
    
    if user and verify_password(user['password'], password):
        session['user_id'] = str(user['_id'])
        session['role'] = user['role']
        session['email'] = user['email']
        
        if user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    
    flash("Invalid email or password", "error")
    return redirect(url_for('login'))

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        branch = request.form.get('branch')
        cgpa = float(request.form.get('cgpa'))
        resume_file = request.files.get('resume')

        if users_collection.find_one({'email': email}):
            flash("Email already registered", "error")
            return redirect(url_for('signup'))

        # Save Resume
        resume_filename = f"{secure_filename(email)}_{secure_filename(resume_file.filename)}"
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
        resume_file.save(resume_path)
        
        # Create User
        user_id = users_collection.insert_one({
            'email': email,
            'password': hash_password(password),
            'role': 'student'
        }).inserted_id
        
        # Create Student Profile
        students_collection.insert_one({
            'user_id': user_id,
            'name': name,
            'branch': branch,
            'cgpa': cgpa,
            'resume_path': resume_filename
        })
        
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    except Exception as e:
        flash(f"Error: {e}", "error")
        return redirect(url_for('signup'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- ADMIN ROUTES ---

@app.route('/admin/dashboard')
@login_required(role='admin')
def admin_dashboard():
    stats = {
        'total_jobs': jobs_collection.count_documents({}),
        'total_students': students_collection.count_documents({}),
        'total_applications': applications_collection.count_documents({})
    }
    
    # Chart Data: Application Status Distribution
    pipeline = [
        {'$group': {'_id': '$status', 'count': {'$sum': 1}}}
    ]
    status_counts = list(applications_collection.aggregate(pipeline))
    chart_data = {item['_id']: item['count'] for item in status_counts}
    # Ensure common statuses exist for the chart
    for status in ['Applied', 'Shortlisted', 'Selected', 'Rejected']:
        if status not in chart_data:
            chart_data[status] = 0

    jobs = list(jobs_collection.find().sort('created_at', -1).limit(5))
    announcements = list(announcements_collection.find().sort('date', -1).limit(5))
    return render_template('admin/dashboard.html', stats=stats, jobs=jobs, announcements=announcements, chart_data=chart_data)

@app.route('/admin/jobs/add', methods=['POST'])
@login_required(role='admin')
def add_job():
    company = request.form.get('company')
    role = request.form.get('role')
    min_cgpa = float(request.form.get('min_cgpa'))
    drive_date = request.form.get('drive_date')
    
    jobs_collection.insert_one({
        'company_name': company,
        'role': role,
        'min_cgpa': min_cgpa,
        'drive_date': drive_date,
        'created_at': datetime.datetime.now()
    })
    
    # Notify all students about the new job
    students = list(students_collection.find({}, {'user_id': 1}))
    notifications = []
    for s in students:
        notifications.append({
            'user_id': s['user_id'],
            'title': f"New Job: {company}",
            'message': f"A new position for '{role}' has been posted. Your Success Match score is updated!",
            'link': '/student/jobs',
            'is_read': False,
            'created_at': datetime.datetime.now()
        })
    if notifications:
        notifications_collection.insert_many(notifications)
        
    flash("Job posted successfully and students notified!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/jobs/manage')
@login_required(role='admin')
def manage_jobs():
    jobs = list(jobs_collection.find().sort('created_at', -1))
    return render_template('admin/manage_jobs.html', jobs=jobs)

@app.route('/admin/jobs/delete/<job_id>', methods=['POST'])
@login_required(role='admin')
def delete_job(job_id):
    jobs_collection.delete_one({'_id': ObjectId(job_id)})
    # Also delete associated applications
    applications_collection.delete_many({'job_id': ObjectId(job_id)})
    flash("Job and associated applications deleted", "success")
    return redirect(url_for('manage_jobs'))

@app.route('/admin/announcements/add', methods=['POST'])
@login_required(role='admin')
def add_announcement():
    title = request.form.get('title')
    content = request.form.get('content')
    
    announcements_collection.insert_one({
        'title': title,
        'content': content,
        'date': datetime.datetime.now()
    })
    
    # Notify all students about the announcement
    students = list(students_collection.find({}, {'user_id': 1}))
    notifications = []
    for s in students:
        notifications.append({
            'user_id': s['user_id'],
            'title': "New Announcement",
            'message': f"{title}: {content[:50]}...",
            'link': '/student/dashboard',
            'is_read': False,
            'created_at': datetime.datetime.now()
        })
    if notifications:
        notifications_collection.insert_many(notifications)
        
    flash("Announcement posted and students notified!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/announcements/manage')
@login_required(role='admin')
def manage_announcements():
    announcements = list(announcements_collection.find().sort('date', -1))
    return render_template('admin/manage_announcements.html', announcements=announcements)

@app.route('/admin/announcements/delete/<ann_id>', methods=['POST'])
@login_required(role='admin')
def delete_announcement(ann_id):
    announcements_collection.delete_one({'_id': ObjectId(ann_id)})
    flash("Announcement deleted", "success")
    return redirect(url_for('manage_announcements'))

@app.route('/admin/applications')
@login_required(role='admin')
def view_applications():
    # Aggregate to get student and job details
    pipeline = [
        {
            '$lookup': {
                'from': 'students',
                'let': {'student_id': '$student_id'},
                'pipeline': [
                    {'$match': {'$expr': {'$eq': ['$user_id', '$$student_id']}}}
                ],
                'as': 'student_info'
            }
        },
        {
            '$lookup': {
                'from': 'jobs',
                'localField': 'job_id',
                'foreignField': '_id',
                'as': 'job_info'
            }
        },
        {'$unwind': '$student_info'},
        {'$unwind': '$job_info'}
    ]
    applications = list(applications_collection.aggregate(pipeline))
    return render_template('admin/applications.html', applications=applications)

@app.route('/admin/applications/update/<app_id>', methods=['POST'])
@login_required(role='admin')
def update_application_status(app_id):
    new_status = request.form.get('status')
    applications_collection.update_one(
        {'_id': ObjectId(app_id)},
        {'$set': {'status': new_status}}
    )
    flash("Status updated", "success")
    return redirect(url_for('view_applications'))

@app.route('/admin/applications/export')
@login_required(role='admin')
def export_applications():
    pipeline = [
        {
            '$lookup': {
                'from': 'students',
                'let': {'student_id': '$student_id'},
                'pipeline': [{'$match': {'$expr': {'$eq': ['$user_id', '$$student_id']}}}],
                'as': 'student_info'
            }
        },
        {
            '$lookup': {
                'from': 'jobs',
                'localField': 'job_id',
                'foreignField': '_id',
                'as': 'job_info'
            }
        },
        {'$unwind': '$student_info'},
        {'$unwind': '$job_info'}
    ]
    apps = list(applications_collection.aggregate(pipeline))
    
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Student Name', 'Email', 'Branch', 'CGPA', 'Company', 'Role', 'Status', 'Applied At'])
    
    for app in apps:
        cw.writerow([
            app['student_info']['name'],
            app['student_info'].get('email', 'N/A'), # session email might not reflect in student doc
            app['student_info']['branch'],
            app['student_info']['cgpa'],
            app['job_info']['company_name'],
            app['job_info']['role'],
            app['status'],
            app['applied_at'].strftime('%Y-%m-%d %H:%M')
        ])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=applications_report.csv"
    output.headers["Content-type"] = "text/csv"
    return output

# --- STUDENT ROUTES ---

@app.route('/student/dashboard')
@login_required(role='student')
def student_dashboard():
    student = students_collection.find_one({'user_id': ObjectId(session['user_id'])})
    if not student:
        flash("Student profile not found", "error")
        return redirect(url_for('logout'))
        
    # Eligible jobs
    eligible_jobs = list(jobs_collection.find({'min_cgpa': {'$lte': student['cgpa']}}).sort('created_at', -1).limit(6))
    
    # Announcements
    announcements = list(announcements_collection.find().sort('date', -1).limit(3))
    
    # My Applications
    pipeline = [
        {
            '$match': {'student_id': ObjectId(session['user_id'])}
        },
        {
            '$lookup': {
                'from': 'jobs',
                'localField': 'job_id',
                'foreignField': '_id',
                'as': 'job_info'
            }
        },
        {'$unwind': '$job_info'},
        {'$sort': {'applied_at': -1}}
    ]
    my_applications = list(applications_collection.aggregate(pipeline))
    applied_job_ids = [app['job_id'] for app in my_applications]

    # Calculate match scores for eligible jobs
    for job in eligible_jobs:
        # Basic scoring: (Student CGPA / 10) * 100
        base_score = (student['cgpa'] / 10.0) * 100
        # Add a 10% bonus if it's a specialized branch match (simulated)
        job['match_score'] = min(100, round(base_score))
    
    return render_template('student/dashboard.html', 
                         student=student, 
                         jobs=eligible_jobs, 
                         announcements=announcements,
                         my_applications=my_applications,
                         applied_job_ids=applied_job_ids)

@app.route('/student/profile')
@login_required(role='student')
def student_profile():
    student = students_collection.find_one({'user_id': ObjectId(session['user_id'])})
    return render_template('student/profile.html', student=student)

@app.route('/student/jobs')
@login_required(role='student')
def student_jobs():
    student = students_collection.find_one({'user_id': ObjectId(session['user_id'])})
    all_jobs = list(jobs_collection.find().sort('created_at', -1))
    
    # My Applications to check status
    my_applications = list(applications_collection.find({'student_id': ObjectId(session['user_id'])}))
    applied_job_ids = [app['job_id'] for app in my_applications]

    # Calculate predictive match scores
    for job in all_jobs:
        cgpa_factor = (student['cgpa'] / 10.0) * 100
        # Simulated bonus for IT/CSE branch alignment
        branch_bonus = 15 if student['branch'].lower() in job['role'].lower() or student['branch'].lower() == 'cse' else 5
        job['match_score'] = min(100, round(cgpa_factor * 0.8 + branch_bonus))
    
    return render_template('student/jobs.html', student=student, jobs=all_jobs, applied_job_ids=applied_job_ids)

@app.route('/student/experiences')
@login_required(role='student')
def view_experiences():
    exps = list(experiences_collection.find().sort('date', -1))
    return render_template('student/experiences.html', experiences=exps)

@app.route('/student/experiences/add', methods=['POST'])
@login_required(role='student')
def add_experience():
    company = request.form.get('company')
    content = request.form.get('content')
    student_name = students_collection.find_one({'user_id': ObjectId(session['user_id'])})['name']
    
    experiences_collection.insert_one({
        'company': company,
        'content': content,
        'student_name': student_name,
        'date': datetime.datetime.now()
    })
    flash("Experience shared successfully!", "success")
    return redirect(url_for('view_experiences'))

@app.route('/api/notifications')
@login_required()
def get_notifications():
    # Only show for students for now, but system is extensible
    user_id = ObjectId(session['user_id'])
    notifications = list(notifications_collection.find({'user_id': user_id}).sort('created_at', -1).limit(10))
    # Convert ObjectIds and Datetimes for JSON
    for n in notifications:
        n['_id'] = str(n['_id'])
        n['user_id'] = str(n['user_id'])
        n['created_at'] = n['created_at'].strftime('%b %d, %H:%M')
    return {'notifications': notifications}

@app.route('/api/notifications/read/<notif_id>', methods=['POST'])
@login_required()
def mark_read(notif_id):
    notifications_collection.update_one(
        {'_id': ObjectId(notif_id), 'user_id': ObjectId(session['user_id'])},
        {'$set': {'is_read': True}}
    )
    return {'status': 'success'}

@app.route('/student/apply/<job_id>', methods=['POST'])
@login_required(role='student')
def apply_job(job_id):
    student_id = ObjectId(session['user_id'])
    job_id = ObjectId(job_id)
    
    # Check if already applied
    if applications_collection.find_one({'student_id': student_id, 'job_id': job_id}):
        flash("You have already applied", "error")
        return redirect(url_for('student_dashboard'))
        
    applications_collection.insert_one({
        'student_id': student_id,
        'job_id': job_id,
        'status': 'Applied',
        'applied_at': datetime.datetime.now()
    })
    flash("Applied successfully!", "success")
    return redirect(url_for('student_dashboard'))

@app.route('/student/update_resume', methods=['POST'])
@login_required(role='student')
def update_resume():
    if 'resume' not in request.files:
        flash("No file part", "error")
        return redirect(url_for('student_dashboard'))
        
    file = request.files['resume']
    if file.filename == '':
        flash("No selected file", "error")
        return redirect(url_for('student_dashboard'))

    if file:
        student = students_collection.find_one({'user_id': ObjectId(session['user_id'])})
        
        # Remove old file
        old_filename = student.get('resume_path')
        if old_filename:
            old_path = os.path.join(app.config['UPLOAD_FOLDER'], old_filename)
            if os.path.exists(old_path):
                os.remove(old_path)
                
        # Save new file
        new_filename = f"{secure_filename(session['email'])}_{secure_filename(file.filename)}"
        new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(new_path)
        
        # Update DB
        students_collection.update_one(
            {'user_id': ObjectId(session['user_id'])},
            {'$set': {'resume_path': new_filename}}
        )
        
        flash("Resume updated successfully!", "success")
        return redirect(url_for('student_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
