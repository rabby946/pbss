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
import traceback, sib_api_v3_sdk, threading
from flask import current_app

def _send_async_email(app, recipient, subject, body, html=False):
    with app.app_context():
        try:
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key["api-key"] = app.config["BREVO_API_KEY"]
            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
            sender = {
                "name": app.config["BREVO_SENDER_NAME"],
                "email": app.config["BREVO_SENDER_EMAIL"],
            }
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=[{"email": r} for r in recipient],subject=subject,sender=sender,html_content=body if html else f"<p>{body}</p>",text_content=None if html else body,)
            api_instance.send_transac_email(send_smtp_email)
            app.logger.info(f"Brevo email sent to {recipient}")
        except Exception as e:
            app.logger.error(f"Brevo email failed: {e}\n{traceback.format_exc()}")

def sendMail(recipient, subject, body):
    if not isinstance(recipient, list):
        recipient = [recipient]
    app = current_app._get_current_object()
    threading.Thread(target=_send_async_email,args=(app, recipient, subject, body, False),daemon=True,).start()
from datetime import datetime
def send_otp_email(to_email, user_name=None):
    otp = str(random.randint(100000, 999999))
    session['reset_otp'] = otp
    session['reset_email'] = to_email

    subject = "Palashbaria Secondary School — Password Reset OTP"

    html_content = f"""
    <html>
      <head>
        <meta charset="UTF-8">
        <title>Password Reset OTP</title>
        <style>
          body {{
            background-color: #f4f6f8;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
          }}
          .container {{
            max-width: 600px;
            margin: 40px auto;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.08);
            overflow: hidden;
          }}
          .header {{
            background-color: #0a4d94;
            color: white;
            text-align: center;
            padding: 20px;
          }}
          .header img {{
            height: 60px;
            margin-bottom: 10px;
          }}
          .content {{
            padding: 30px;
            color: #333333;
            line-height: 1.6;
          }}
          .otp-box {{
            background-color: #f0f7ff;
            border: 2px solid #0a4d94;
            border-radius: 8px;
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            color: #0a4d94;
            letter-spacing: 3px;
            margin: 25px auto;
            padding: 15px 0;
            width: 60%;
          }}
          .footer {{
            background-color: #f9f9f9;
            text-align: center;
            font-size: 12px;
            color: #888888;
            padding: 15px;
          }}
          a {{
            color: #0a4d94;
            text-decoration: none;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <img src="https://palashbariasecondaryschool.org/static/images/logo.png" alt="Palashbaria Secondary School Logo">
            <h2>Palashbaria Secondary School</h2>
          </div>
          <div class="content">
            <p>Dear {user_name or 'User'},</p>
            <p>You recently requested to reset your password for your school account. Please use the following One-Time Password (OTP) to complete the process:</p>

            <div class="otp-box">{otp}</div>

            <p>This OTP will expire in <strong>5 minutes</strong>.</p>
            <p>If you did not request this password reset, please ignore this email or contact school support immediately.</p>

            <p>Best regards,<br>
            <strong>Palashbaria Secondary School IT Team</strong></p>
          </div>
          <div class="footer">
            <p>&copy; {datetime.now().year} Palashbaria Secondary School | <a href="https://palashbariasecondaryschool.org">Visit Website</a></p>
          </div>
        </div>
      </body>
    </html>
    """

    sendMail(to_email, subject, html_content)
    return otp
