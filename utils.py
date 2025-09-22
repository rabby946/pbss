import cloudinary.uploader
from functools import wraps
from flask import session, redirect, url_for, flash
from config import Config


# ---------------------------
# Admin Login Protection
# ---------------------------
def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('admin'):
            flash("Login required", "error")
            return redirect(url_for('admin.login'))
        return view(*args, **kwargs)
    return wrapped


# ---------------------------
# Upload to Cloudinary
# ---------------------------
def upload_to_imgbb(file, folder="uploads"):
    """
    Upload file to Cloudinary and return its viewable URL.
    
    Args:
        file: FileStorage object from Flask (request.files['image'])
        folder: Cloudinary folder name (default: 'uploads')
    
    Returns:
        str: Secure URL of the uploaded image
    """
    if not file:
        raise ValueError("No file provided for upload")

    try:
        result = cloudinary.uploader.upload(file, folder=folder)
        return result["secure_url"]   # Always returns HTTPS link
    except Exception as e:
        raise ValueError(f"Cloudinary upload failed: {e}")
