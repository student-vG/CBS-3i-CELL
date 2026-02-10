import csv
from io import StringIO
from flask import make_response
import datetime

def generate_student_export(students):
    """
    Generates a comprehensive CSV file from all student documents.
    Matches dashboard data exactly with all academic and personal details.
    """
    si = StringIO()
    cw = csv.writer(si)
    
    # Comprehensive Header matching dashboard data
    headers = [
        'Student ID', 'Full Name', 'Email', 'Phone', 'Gender', 
        'Date of Birth', 'Aadhaar Number', 'PAN',
        '10th School', '10th Board', '10th Year', '10th Percentage',
        '12th School', '12th Board', '12th Year', '12th Percentage', '12th Stream',
        'UG College', 'UG University', 'UG Degree', 'UG Branch', 'UG Year', 'UG CGPA', 'UG Backlogs', 'UG Backlog Status',
        'PG College', 'PG University', 'PG Degree', 'PG Branch', 'PG Year', 'PG CGPA', 'PG Backlogs', 'PG Backlog Status',
        'Skills', 'Projects', 'Branch', 'CGPA', 'Status', 'Registered At'
    ]
    cw.writerow(headers)
    
    # Data
    for s in students:
        # Extract academic info safely
        academic = s.get('academic', {})
        tenth = academic.get('tenth', {})
        twelfth = academic.get('twelfth', {})
        ug = academic.get('ug', {})
        pg = academic.get('pg', {})
        
        # Get user email from users collection if needed
        from utils.db import get_db
        db = get_db()
        user = db.users.find_one({'_id': s.get('user_id')})
        email = user.get('email', 'N/A') if user else 'N/A'
        
        cw.writerow([
            s.get('student_id', 'N/A'),
            s.get('name', 'N/A'),
            email,
            s.get('phone', 'N/A'),
            s.get('gender', 'N/A'),
            s.get('dob', 'N/A'),
            s.get('aadhaar', 'N/A'),
            s.get('pan', 'N/A'),
            # 10th
            tenth.get('school', ''),
            tenth.get('board', ''),
            tenth.get('year', ''),
            tenth.get('score', ''),
            # 12th
            twelfth.get('school', ''),
            twelfth.get('board', ''),
            twelfth.get('year', ''),
            twelfth.get('score', ''),
            twelfth.get('stream', ''),
            # UG
            ug.get('college', ''),
            ug.get('university', ''),
            ug.get('degree', ''),
            ug.get('branch', ''),
            ug.get('year', ''),
            ug.get('score', ''),
            ug.get('backlogs', 0),
            ug.get('backlog_status', ''),
            # PG
            pg.get('college', ''),
            pg.get('university', ''),
            pg.get('degree', ''),
            pg.get('branch', ''),
            pg.get('year', ''),
            pg.get('score', ''),
            pg.get('backlogs', 0),
            pg.get('backlog_status', ''),
            # Skills & Projects
            ", ".join(s.get('skills', [])),
            s.get('projects', ''),
            # Quick filters
            s.get('branch', 'N/A'),
            s.get('cgpa', 0.0),
            'Active' if s.get('is_active') else 'Inactive',
            s.get('registered_at', '').strftime('%Y-%m-%d') if s.get('registered_at') else 'N/A'
        ])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=students_export.csv"
    output.headers["Content-type"] = "text/csv"
    return output


def generate_application_export(applications, job_title="All_Applications"):
    """
    Generates a comprehensive CSV file for job applications.
    Includes auto-filled student data + job-specific data + multiple application flag.
    """
    si = StringIO()
    cw = csv.writer(si)
    
    # Comprehensive headers matching admin dashboard
    headers = [
        'Student Name', 'Student ID', 'Email', 'Phone', 'Branch', 'CGPA',
        'Company', 'Job Role', 'Applied Date', 'Status',
        'Student Response', 'Response Date',
        'Multiple Applications', 'Skills'
    ]
    cw.writerow(headers)
    
    for app in applications:
        # Extract student info
        student_info = app.get('student_info', [{}])[0] if app.get('student_info') else {}
        user_info = app.get('user_info', [{}])[0] if app.get('user_info') else {}
        job_info = app.get('job_info', [{}])[0] if app.get('job_info') else {}
        
        # Multiple application flag
        is_multiple = 'YES' if app.get('is_multiple_applicant') else 'NO'
        
        # Response handling
        response = app.get('student_response', 'Pending')
        response_date = app.get('response_at', '')
        if response_date:
            if hasattr(response_date, 'strftime'):
                response_date = response_date.strftime('%Y-%m-%d %H:%M')
        else:
            response_date = 'N/A'
        
        applied_date = app.get('applied_at', '')
        if applied_date:
            if hasattr(applied_date, 'strftime'):
                applied_date = applied_date.strftime('%Y-%m-%d %H:%M')
        else:
            applied_date = 'N/A'
        
        cw.writerow([
            app.get('student_name', 'N/A'),
            student_info.get('student_id', 'N/A'),
            user_info.get('email', 'N/A'),
            student_info.get('phone', 'N/A'),
            student_info.get('branch', 'N/A'),
            student_info.get('cgpa', 0.0),
            job_info.get('company_name', 'N/A'),
            job_info.get('role', 'N/A'),
            applied_date,
            app.get('status', 'Pending'),
            response,
            response_date,
            is_multiple,
            ", ".join(student_info.get('skills', []))
        ])
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=applications_{job_title.replace(' ', '_')}.csv"
    output.headers["Content-type"] = "text/csv"
    return output
