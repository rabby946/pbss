from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Subject, SchoolClass, Gallery, AssignedSubject
from datetime import datetime
from . import admin_bp
from utils import admin_required, upload_image

from flask import render_template, request, redirect, url_for, flash
from datetime import datetime
from . import admin_bp
from models import db, Routine, SchoolClass, Teacher, Subject
from utils import admin_required


@admin_bp.route("/routines", methods=["GET", "POST"])
@admin_required
def manage_routines():
    # Filtering
    selected_day = request.args.get("day", "all")
    selected_class = request.args.get("class_id", "all")

    query = Routine.query.join(Subject).join(SchoolClass)

    if selected_day != "all":
        query = query.filter(Routine.day == selected_day)
    if selected_class != "all":
        query = query.filter(Subject.class_id == selected_class)

    routines = query.order_by(Routine.start_time.asc()).all()

    # Dropdown data
    days = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    classes = SchoolClass.query.order_by(SchoolClass.name).all()
    subjects = Subject.query.order_by(Subject.name).all()
    teachers = Teacher.query.order_by(Teacher.name).all()

    return render_template(
        "admin/routines.html",
        routines=routines,
        days=days,
        classes=classes,
        teachers=teachers,
        subjects=subjects,
        selected_day=selected_day,
        selected_class=selected_class
    )


@admin_bp.route("/routine/add", methods=["POST"])
@admin_required
def add_routine():
    try:
        subject_id = request.form.get("subject_id")
        day = request.form.get("day")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        room = request.form.get("room")
        print(99)
        if not all([subject_id, day, start_time, end_time]):
            flash("All fields are required.", "danger")
            return redirect(url_for("admin_bp.manage_routines"))

        subject_id = int(subject_id)
        sub = Subject.query.get_or_404(subject_id)

        # 🔍 Find the active teacher assigned to this subject
        assign = AssignedSubject.query.filter_by(subject_id=subject_id, status="active").first()
        if not assign:
            flash("This subject is not assigned to any teacher. Assign it first.", "danger")
            return redirect(url_for("admin_bp.manage_routines"))

        teacher_id = assign.teacher_id  # ✅ Automatically use assigned teacher
        class_id = sub.class_id

        # Convert times
        start_time = datetime.strptime(start_time, "%H:%M").time()
        end_time = datetime.strptime(end_time, "%H:%M").time()

        # Calculate duration
        duration = (
            datetime.combine(datetime.today(), end_time)
            - datetime.combine(datetime.today(), start_time)
        ).seconds // 60

        # 🧠 Optional: prevent duplicate same-day same-time routine for same subject
        existing = Routine.query.filter_by(
            subject_id=subject_id, day=day, start_time=start_time
        ).first()
        if existing:
            flash("A routine already exists for this subject at the same time.", "warning")
            return redirect(url_for("admin_bp.manage_routines"))

        # Add routine
        new_routine = Routine(
            teacher_id=teacher_id,
            subject_id=subject_id,
            day=day,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            room=room,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.session.add(new_routine)
        db.session.commit()
        flash("Routine added successfully!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error adding routine: {str(e)}", "danger")

    return redirect(url_for("admin_bp.manage_routines"))


@admin_bp.route("/routine/delete/<int:id>")
@admin_required
def delete_routine(id):
    routine = Routine.query.get_or_404(id)
    try:
        db.session.delete(routine)
        db.session.commit()
        flash("Routine deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting routine: {e}", "danger")

    return redirect(url_for("admin_bp.manage_routines"))
