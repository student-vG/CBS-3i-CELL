import functools
from flask import session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password):
    return generate_password_hash(password)

def verify_password(hashed_password, password):
    return check_password_hash(hashed_password, password)

def login_required(role=None):
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            if role and session.get('role') != role:
                flash("Unauthorized access", "error")
                # Redirect based on their actual role or home
                if session.get('role') == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif session.get('role') == 'student':
                    return redirect(url_for('student_dashboard'))
                return redirect(url_for('login'))
                
            return f(*args, **kwargs)
        return wrapped
    return decorator
