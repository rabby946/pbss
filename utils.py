from functools import wraps
from flask import session, redirect, url_for, flash
import requests, base64
from config import Config

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('admin'):
            flash("Login required", "error")
            return redirect(url_for('admin.login'))
        return view(*args, **kwargs)
    return wrapped

def upload_to_imgbb(file):
    """Upload file to ImageBB and return URL"""
    encoded_image = base64.b64encode(file.read()).decode("utf-8")
    response = requests.post(
        "https://api.imgbb.com/1/upload",
        data={"key": Config.IMGBB_API_KEY, "image": encoded_image}
    )
    if response.status_code == 200:
        return response.json()['data']['url']
    else:
        raise ValueError(f"Image upload failed: {response.text}")
