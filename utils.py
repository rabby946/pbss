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
   

asasease
