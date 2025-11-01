import cloudinary.uploader
from functools import wraps
from flask import session, redirect, url_for, flash
from config import Config
import random
from flask import session, flash, redirect, url_for, request, render_template
import requests, os
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


import os
import random
import requests
from flask import session

BREVO_API_KEY = os.getenv("BREVO_API_KEY")

def send_otp_email(to_email, user_name=None):
    otp = str(random.randint(100000, 999999))
    session['reset_otp'] = otp
    session['reset_email'] = to_email
    print(otp)
    sender = {
        "name": "Palashbaria School",
        "email": "no-reply@yourdomain.com"  # ensure you have this sender verified in Brevo
    }
    to = [
        {
          "email": to_email,
          "name": user_name or ""
        }
    ]
    subject = "Your Password Reset OTP"
    html_content = f"""
    <html>
      <body>
        <p>Hi {user_name or ''},</p>
        <p>Your password reset OTP is <strong>{otp}</strong>. It will expire in 5 minutes.</p>
        <p>If you did not request this, please ignore this email.</p>
      </body>
    </html>
    """
    payload = {
      "sender": sender,
      "to": to,
      "subject": subject,
      "htmlContent": html_content
    }
    headers = {
      "accept": "application/json",
      "api-key": BREVO_API_KEY,
      "content-type": "application/json"
    }
    url = "https://api.brevo.com/v3/smtp/email"
    response = requests.post(url, json=payload, headers=headers)
    # print("Sent OTP email to", to_email, "response:", response.json())
    return otp
