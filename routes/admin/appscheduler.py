# routes/admin/class_management.py
from operator import and_, not_
from flask import render_template, request, redirect, url_for, flash
from . import admin_bp
from models import Teacher, db, TeacherAttendance
from utils import admin_required
from datetime import datetime, timedelta
from sqlalchemy import and_, not_

@admin_bp.route("/appscheduler")
def app_scheduler():
    bd_now = datetime.utcnow() + timedelta(hours=6)
    bd_time = bd_now.time()
    bd_date = bd_now.date()
    if bd_time < datetime.strptime("15:00", "%H:%M").time():
        return f'Good day!'
    attendance = TeacherAttendance.query.filter(TeacherAttendance.status == "absent",TeacherAttendance.date == bd_date).first()
    if attendance:
        return f'Good evening!'
    attended_ids = db.session.query(TeacherAttendance.teacher_id).filter(
        and_(
            TeacherAttendance.date == bd_date,
            TeacherAttendance.status.in_(["present", "late"])
        )
    ).all()
    attended_ids = {tid for (tid,) in attended_ids}  

    if not attended_ids:
        return "Holiday: no one present, nothing marked"

    absent_teachers = db.session.query(Teacher).filter(
        not_(Teacher.id.in_(attended_ids))
    ).all()

    for teacher in absent_teachers:
        absent_record = TeacherAttendance(
            teacher_id=teacher.id,
            status="absent",
            date=bd_date
        )
        db.session.add(absent_record)

    db.session.commit()
    return f"Marked {len(absent_teachers)} teachers as absent"


