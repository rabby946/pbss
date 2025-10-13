import cloudinary.uploader
from functools import wraps
from flask import session, redirect, url_for, flash
from config import Config
def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('admin'):
            flash("Login required", "error")
            return redirect(url_for('admin_bp.login'))
        return view(*args, **kwargs)
    return wrapped

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
            flash("Please log in as a student to access this page.", "warning")
            return redirect(url_for('public.login'))
        return f(*args, **kwargs)
    return decorated_function


def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'teacher_id' not in session:
            flash("Please log in as a teacher to access this page.", "warning")
            return redirect(url_for('public.login'))
        return f(*args, **kwargs)
    return decorated_function

def upload_image(file, folder="uploads"):
    if not file:
        raise ValueError("No file provided for upload")
    try:
        result = cloudinary.uploader.upload(file, folder=folder)
        return result["secure_url"]   # Always returns HTTPS link
    except Exception as e:
        raise ValueError(f"Cloudinary upload failed: {e}")
