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
   

import requests

def upload_to_imgbb(file, expiration=None):
    """Upload file to ImgBB and return the image URL."""
    data = {"key": Config.IMGBB_API_KEY}
    if expiration:
        data["expiration"] = expiration

    response = requests.post(
        "https://api.imgbb.com/1/upload",
        data=data,
        files={"image": file}
    )

    if response.status_code == 200:
        return response.json()["data"]["url"]
    else:
        raise ValueError(f"Image upload failed: {response.text}")
