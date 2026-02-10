from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response, current_app
from utils.db import get_db, get_fs
from bson.objectid import ObjectId
import datetime
import csv
import io

dynamic_forms_bp = Blueprint('dynamic_forms', __name__)

@dynamic_forms_bp.route('/admin/forms/create', methods=['GET', 'POST'])
def create_form():
    if session.get('role') not in ['admin', 'faculty']:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        db = get_db()
        title = request.form.get('title')
        description = request.form.get('description')
        
        # Process fields dynamically
        # Expected format from frontend: field_label_1, field_type_1, field_required_1, etc.
        # This part requires a specific frontend implementation (e.g., JS sending JSON or structured form data)
        # For simplicity, let's assume the frontend sends a JSON string or we parse indexed keys if we build a standard form.
        # Let's try to parse complex form data or assume a JS fetch approach that sends JSON. 
        # But to stick with standard Flask forms, let's look for known keys or iterate.
        
        # Actually, standard way is to generic Javascript to create hidden inputs or similar. 
        # Let's grab the fields from a hidden JSON input which is easier to manage with frontend JS builder.
        import json
        fields_json = request.form.get('fields_data')
        
        try:
            fields = json.loads(fields_json) if fields_json else []
        except:
            flash("Invalid form data structure", "error")
            return redirect(url_for('dynamic_forms.create_form'))

        form_data = {
            'title': title,
            'description': description,
            'fields': fields,
            'created_by': session.get('user_id'),
            'created_at': datetime.datetime.utcnow(),
            'is_active': True
        }
        
        db.forms.insert_one(form_data)
        
        # Auto-create announcement to notify students
        announcement = {
            'title': f"New Form: {title}",
            'content': f"A new form '{title}' has been assigned. Please fill it out at your earliest convenience.\n{description[:100]}...",
            'created_by': session.get('user_id'),
            'created_at': datetime.datetime.utcnow()
        }
        db.announcements.insert_one(announcement)
        
        flash("Form created and students notified via announcement!", "success")
        return redirect(url_for('dynamic_forms.manage_forms'))
        
    return render_template('admin/create_form.html')

@dynamic_forms_bp.route('/admin/forms')
def manage_forms():
    if session.get('role') not in ['admin', 'faculty']:
        return redirect(url_for('login'))
        
    db = get_db()
    forms = list(db.forms.find().sort('created_at', -1))
    return render_template('admin/manage_forms.html', forms=forms)

@dynamic_forms_bp.route('/admin/forms/toggle/<form_id>', methods=['POST'])
def toggle_form(form_id):
    if session.get('role') not in ['admin', 'faculty']:
        return redirect(url_for('login'))
    
    db = get_db()
    form = db.forms.find_one({'_id': ObjectId(form_id)})
    if form:
        new_status = not form.get('is_active', True)
        db.forms.update_one({'_id': ObjectId(form_id)}, {'$set': {'is_active': new_status}})
        flash(f"Form {'activated' if new_status else 'deactivate'} successfully", "success")
    
    return redirect(url_for('dynamic_forms.manage_forms'))

@dynamic_forms_bp.route('/student/forms')
def list_student_forms():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
        
    db = get_db()
    # List all forms (active and inactive)
    forms = list(db.forms.find().sort('created_at', -1))
    
    # Check which ones the student has already submitted
    submitted_ids = [
        resp['form_id'] for resp in db.form_responses.find(
            {'student_id': session.get('user_id')}, 
            {'form_id': 1}
        )
    ]
    
    # Get student's submitted form responses for display
    my_responses = list(db.form_responses.find(
        {'student_id': session.get('user_id')}
    ).sort('submitted_at', -1))
    
    return render_template('student/forms_list.html', forms=forms, submitted_ids=submitted_ids, my_responses=my_responses)

@dynamic_forms_bp.route('/student/forms/<form_id>', methods=['GET', 'POST'])
def fill_form(form_id):
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
        
    db = get_db()
    form = db.forms.find_one({'_id': ObjectId(form_id)})
    
    if not form or not form.get('is_active'):
        flash("Form not found or inactive", "error")
        return redirect(url_for('dynamic_forms.list_student_forms'))
        
    # Check if already submitted
    existing = db.form_responses.find_one({
        'form_id': ObjectId(form_id), 
        'student_id': session.get('user_id')
    })
    if existing:
        flash("You have already submitted this form.", "info")
        return redirect(url_for('dynamic_forms.list_student_forms'))

    if request.method == 'POST':
        answers = {}
        fs = get_fs()
        
        for field in form.get('fields', []):
            label = field.get('label')
            field_type = field.get('type')
            
            if field_type == 'file':
                if label in request.files:
                    file = request.files[label]
                    if file and file.filename:
                        # Upload to GridFS
                        file_id = fs.put(file, filename=file.filename, content_type=file.content_type)
                        answers[label] = str(file_id) # Store ID reference
                    else:
                        # Handle required check if needed, though HTML5 required usually catches this
                        pass 
            else:
                answers[label] = request.form.get(label)
                
        response_data = {
            'form_id': ObjectId(form_id),
            'student_id': session.get('user_id'),
            'student_name': session.get('name', 'Unknown'), # Cache name for easier export
            'answers': answers,
            'submitted_at': datetime.datetime.utcnow()
        }
        
        db.form_responses.insert_one(response_data)
        flash("Form submitted successfully!", "success")
        return redirect(url_for('dynamic_forms.list_student_forms'))
        
    return render_template('student/fill_form.html', form=form)

@dynamic_forms_bp.route('/admin/forms/<form_id>/export')
def export_form_responses(form_id):
    if session.get('role') not in ['admin', 'faculty']:
        return redirect(url_for('login'))
        
    db = get_db()
    form = db.forms.find_one({'_id': ObjectId(form_id)})
    if not form:
        abort(404)
        
    responses = list(db.form_responses.find({'form_id': ObjectId(form_id)}))
    
    # Generate CSV
    si = io.StringIO()
    cw = csv.writer(si)
    
    # Header: Student Name, Submission Date, [Field Labels...]
    field_labels = [f['label'] for f in form.get('fields', [])]
    header = ['Student Name', 'Submitted At'] + field_labels
    cw.writerow(header)
    
    for resp in responses:
        row = [
            resp.get('student_name', 'N/A'),
            resp.get('submitted_at', '').strftime('%Y-%m-%d %H:%M') if isinstance(resp.get('submitted_at'), datetime.datetime) else str(resp.get('submitted_at', ''))
        ]
        
        answers = resp.get('answers', {})
        for label in field_labels:
            val = answers.get(label, '')
            # If it looks like a GridFS ID (24 hex chars), maybe append a download link?
            # For now, just raw text.
            row.append(val)
            
        cw.writerow(row)
        
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={form['title']}_responses.csv"}
    )

@dynamic_forms_bp.route('/admin/forms/delete/<form_id>', methods=['POST'])
def delete_form(form_id):
    if session.get('role') not in ['admin', 'faculty']:
        return redirect(url_for('login'))
        
    db = get_db()
    # Delete the form
    db.forms.delete_one({'_id': ObjectId(form_id)})
    # Delete associated responses
    db.form_responses.delete_many({'form_id': ObjectId(form_id)})
    
    flash("Form and all its responses deleted successfully.", "success")
    return redirect(url_for('dynamic_forms.manage_forms'))

@dynamic_forms_bp.route('/admin/forms/edit/<form_id>', methods=['GET', 'POST'])
def edit_form(form_id):
    if session.get('role') not in ['admin', 'faculty']:
        return redirect(url_for('login'))
        
    db = get_db()
    form = db.forms.find_one({'_id': ObjectId(form_id)})
    if not form:
        flash("Form not found", "error")
        return redirect(url_for('dynamic_forms.manage_forms'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        import json
        fields_json = request.form.get('fields_data')
        
        try:
            fields = json.loads(fields_json) if fields_json else []
        except:
            flash("Invalid form data structure", "error")
            return redirect(url_for('dynamic_forms.edit_form', form_id=form_id))

        update_data = {
            'title': title,
            'description': description,
            'fields': fields,
            'updated_at': datetime.datetime.utcnow()
        }
        
        db.forms.update_one({'_id': ObjectId(form_id)}, {'$set': update_data})
        flash("Form updated successfully!", "success")
        return redirect(url_for('dynamic_forms.manage_forms'))
        
    return render_template('admin/edit_form.html', form=form)

@dynamic_forms_bp.route('/admin/forms/<form_id>/responses')
def view_form_responses(form_id):
    if session.get('role') not in ['admin', 'faculty']:
        return redirect(url_for('login'))
        
    db = get_db()
    form = db.forms.find_one({'_id': ObjectId(form_id)})
    if not form:
        flash("Form not found", "error")
        return redirect(url_for('dynamic_forms.manage_forms'))
        
    responses = list(db.form_responses.find({'form_id': ObjectId(form_id)}).sort('submitted_at', -1))
    
    # Enrichment: If student_name is Unknown, try to fetch it
    student_ids = [resp['student_id'] for resp in responses if str(resp.get('student_id'))]
    if student_ids:
        # bulk fetch
        # Convert string IDs back to ObjectId if needed, though they are likely already ObjectIds or strings
        # Let's handle both.
        s_ids = []
        for sid in student_ids:
            try:
                s_ids.append(ObjectId(sid))
            except:
                pass
                
        students = list(db.students.find({'user_id': {'$in': s_ids}}))
        student_map = {str(s['user_id']): s.get('name', 'Unknown') for s in students}
        
        # Also map from users collection just in case
        users = list(db.users.find({'_id': {'$in': s_ids}}))
        user_map = {str(u['_id']): u.get('full_name', '') or u.get('name', '') for u in users}

        for resp in responses:
            if resp.get('student_name') == 'Unknown' or not resp.get('student_name'):
                sid = str(resp.get('student_id'))
                # Try student map then user map
                name = student_map.get(sid) or user_map.get(sid) or 'Unknown'
                resp['student_name'] = name # Update in memory for display
    
    return render_template('admin/form_responses.html', form=form, responses=responses)
