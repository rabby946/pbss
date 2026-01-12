# routes/admin/__init__.py
from flask import Blueprint

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")

# Import route files (auto-registers all admin routes)
from . import (
    appscheduler,
    dashboard,
    teacher_management,
    student_management,
    class_management,
    subject_management,
    result_management,
    routine_management,
    attendance_management,
    committee_management,
)
