# app.py - Template Update Snippets

## Replace these route handlers in your app.py:

### 1. Admin Dashboard Route

Replace this:

```python
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    admin_level = session.get('admin_level')

    total_students = students_collection.count_documents({'is_approved': True})
    total_jobs = jobs_collection.count_documents({})
    total_applications = applications_collection.count_documents({})

    stats = {
        'total_students': total_students,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'pending_approvals': students_collection.count_documents({'is_approved': False}) +
                           (users_collection.count_documents({'role': 'admin', 'is_approved': False}) if admin_level == 'super_admin' else 0)
    }

    return render_template('admin/dashboard.html', stats=stats, admin_level=admin_level)
```

With this:

```python
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    admin_level = session.get('admin_level')

    total_students = students_collection.count_documents({'is_approved': True})
    total_jobs = jobs_collection.count_documents({})
    total_applications = applications_collection.count_documents({})

    stats = {
        'total_students': total_students,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'pending_approvals': students_collection.count_documents({'is_approved': False}) +
                           (users_collection.count_documents({'role': 'admin', 'is_approved': False}) if admin_level == 'super_admin' else 0)
    }

    return render_template('admin/dashboard_new.html', stats=stats, admin_level=admin_level)  # ← Changed template name
```

---

### 2. Manage Jobs Route

Replace this:

```python
@app.route('/admin/manage-jobs')
def manage_jobs():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    jobs = list(jobs_collection.find({}))
    return render_template('admin/manage_jobs.html', jobs=jobs)
```

With this:

```python
@app.route('/admin/manage-jobs')
def manage_jobs():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    jobs = list(jobs_collection.find({}))
    # Add applications count to each job
    for job in jobs:
        job['applications_count'] = applications_collection.count_documents({'job_id': job['_id']})

    return render_template('admin/manage_jobs_new.html', jobs=jobs)  # ← Changed template name
```

---

### 3. Manage Announcements Route

Replace this:

```python
@app.route('/admin/manage-announcements')
def manage_announcements():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    announcements = list(announcements_collection.find({}))
    return render_template('admin/manage_announcements.html', announcements=announcements)
```

With this:

```python
@app.route('/admin/manage-announcements')
def manage_announcements():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    announcements = list(announcements_collection.find({}))
    announcements.sort(key=lambda x: x.get('date'), reverse=True)  # Most recent first

    return render_template('admin/manage_announcements_new.html', announcements=announcements)  # ← Changed template name
```

---

### 4. Add Missing Routes (if not present)

Add these routes if they don't exist:

```python
@app.route('/admin/create-job', methods=['POST'])
@login_required
def create_job():
    """Create a new job posting"""
    if session.get('role') != 'admin':
        return {'error': 'Unauthorized'}, 403

    company_name = request.form.get('company_name')
    role = request.form.get('role')
    min_cgpa = float(request.form.get('min_cgpa', 0))
    drive_date = request.form.get('drive_date')
    package = request.form.get('package')
    description = request.form.get('description')

    if not all([company_name, role, drive_date, package, description]):
        flash('All fields are required', 'error')
        return redirect(url_for('manage_jobs'))

    job_data = {
        'company_name': company_name,
        'role': role,
        'min_cgpa': min_cgpa,
        'drive_date': drive_date,
        'package': package,
        'description': description,
        'created_at': datetime.datetime.now(),
        'created_by': ObjectId(session['user_id']),
        'is_active': True
    }

    result = jobs_collection.insert_one(job_data)

    # Notify students
    notifications_collection.insert_many([
        {
            'user_id': student['_id'],
            'title': f"🎉 New Job - {company_name}",
            'message': f"{role} position at {company_name} ({package}). CGPA requirement: {min_cgpa}+",
            'link': url_for('student_jobs'),
            'is_read': False,
            'created_at': datetime.datetime.now(),
            'type': 'job_posting'
        }
        for student in students_collection.find({'is_approved': True})
    ])

    flash(f'Job posted successfully! {company_name} - {role}', 'success')
    return redirect(url_for('manage_jobs'))


@app.route('/admin/create-announcement', methods=['POST'])
@login_required
def create_announcement():
    """Create a new announcement"""
    if session.get('role') != 'admin':
        return {'error': 'Unauthorized'}, 403

    title = request.form.get('title')
    content = request.form.get('content')

    if not all([title, content]):
        flash('Title and content are required', 'error')
        return redirect(url_for('manage_announcements'))

    announcement_data = {
        'title': title,
        'content': content,
        'date': datetime.datetime.now(),
        'created_by': ObjectId(session['user_id']),
        'is_active': True
    }

    result = announcements_collection.insert_one(announcement_data)

    # Notify all students
    notifications_collection.insert_many([
        {
            'user_id': student['_id'],
            'title': f"📢 {title}",
            'message': content[:100] + ('...' if len(content) > 100 else ''),
            'link': url_for('student_dashboard'),
            'is_read': False,
            'created_at': datetime.datetime.now(),
            'type': 'announcement'
        }
        for student in students_collection.find({'is_approved': True})
    ])

    flash('Announcement posted successfully!', 'success')
    return redirect(url_for('manage_announcements'))


@app.route('/admin/edit-job/<job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    """Edit a job posting"""
    if session.get('role') != 'admin':
        return {'error': 'Unauthorized'}, 403

    job = jobs_collection.find_one({'_id': ObjectId(job_id)})

    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('manage_jobs'))

    if request.method == 'POST':
        company_name = request.form.get('company_name')
        role = request.form.get('role')
        min_cgpa = float(request.form.get('min_cgpa', 0))
        drive_date = request.form.get('drive_date')
        package = request.form.get('package')
        description = request.form.get('description')

        jobs_collection.update_one(
            {'_id': ObjectId(job_id)},
            {'$set': {
                'company_name': company_name,
                'role': role,
                'min_cgpa': min_cgpa,
                'drive_date': drive_date,
                'package': package,
                'description': description,
                'updated_at': datetime.datetime.now()
            }}
        )

        flash('Job updated successfully', 'success')
        return redirect(url_for('manage_jobs'))

    return render_template('admin/edit_job.html', job=job)


@app.route('/admin/edit-announcement/<ann_id>', methods=['GET', 'POST'])
@login_required
def edit_announcement(ann_id):
    """Edit an announcement"""
    if session.get('role') != 'admin':
        return {'error': 'Unauthorized'}, 403

    announcement = announcements_collection.find_one({'_id': ObjectId(ann_id)})

    if not announcement:
        flash('Announcement not found', 'error')
        return redirect(url_for('manage_announcements'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        announcements_collection.update_one(
            {'_id': ObjectId(ann_id)},
            {'$set': {
                'title': title,
                'content': content,
                'updated_at': datetime.datetime.now()
            }}
        )

        flash('Announcement updated successfully', 'success')
        return redirect(url_for('manage_announcements'))

    return render_template('admin/edit_announcement.html', announcement=announcement)
```

---

## Summary of Changes

| Function             | Old Template                    | New Template                        | Notes                                |
| -------------------- | ------------------------------- | ----------------------------------- | ------------------------------------ |
| admin_dashboard      | admin/dashboard.html            | admin/dashboard_new.html            | Added stats calculation              |
| manage_jobs          | admin/manage_jobs.html          | admin/manage_jobs_new.html          | Added applications count             |
| manage_announcements | admin/manage_announcements.html | admin/manage_announcements_new.html | Added sorting                        |
| create_job           | N/A                             | N/A                                 | NEW - Implement job creation         |
| create_announcement  | N/A                             | N/A                                 | NEW - Implement announcement         |
| edit_job             | N/A                             | N/A                                 | NEW - Implement job editing          |
| edit_announcement    | N/A                             | N/A                                 | NEW - Implement announcement editing |

---

## Testing Template Routes

After making changes, test these URLs:

1. **Admin Dashboard**: `/admin/dashboard`
2. **Job Management**: `/admin/manage-jobs`
3. **Announcements**: `/admin/manage-announcements`
4. **Student Dashboard**: `/student/dashboard`

Verify each loads the new responsive layout correctly.

---

## Important Notes

1. **@login_required decorator** - Make sure you have this imported from utils.auth
2. **datetime module** - Must be imported at top of app.py
3. **ObjectId** - Must be imported from bson
4. **Collections** - All collections (jobs, announcements, notifications) must be initialized
5. **Error handling** - Forms include basic validation; add more as needed
6. **Notifications** - Job/announcement posting now notifies relevant users

---

Ready to integrate? Follow these steps:

1. Copy code snippets above
2. Update your app.py routes
3. Save file
4. Test routes in browser
5. Fix any issues
6. Deploy!

Need help? Check INTEGRATION-GUIDE.md for troubleshooting.
