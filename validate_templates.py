from flask import Flask
from jinja2 import Environment, FileSystemLoader

app = Flask(__name__)
env = Environment(loader=FileSystemLoader('templates'))

def check_template(template_name):
    try:
        env.get_template(template_name)
        print(f"OK: {template_name}")
    except Exception as e:
        print(f"ERROR: {template_name}: {e}")

print("Checking Templates...")
check_template('admin/dashboard.html')
check_template('student/dashboard.html')
check_template('admin/manage_jobs.html')
check_template('admin/manage_announcements.html')
