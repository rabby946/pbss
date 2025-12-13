from flask import render_template, request, redirect, url_for, flash, current_app
from . import admin_bp
from models import Teacher, User, db, AssignedSubject, Subject, Routine
from datetime import datetime
import random
from werkzeug.utils import secure_filename
from utils import upload_image  , admin_required
@admin_bp.route('/teachers')
def list_teachers():
    teachers = Teacher.query.filter(Teacher.position != "0").order_by(Teacher.position.asc()).all()
    return render_template('admin/teachers.html', teachers=teachers)

@admin_bp.route('/teachers/add', methods=['GET', 'POST'])
@admin_required
def add_teacher():
    if request.method == 'POST':
        try:
            name = request.form['name']
            phone = request.form['phone']
            position = request.form['position']

            # Optional fields
            designation = request.form.get('designation')
            qualification = request.form.get('qualification')
            address = request.form.get('address')
            email = request.form.get('email')
            password = request.form.get('password')

            image_file = request.files.get('image')
            image_url = upload_image(image_file) if image_file else None

            user = User(email=email, password=password, user_type='teacher')
            db.session.add(user)
            db.session.flush()

            teacher = Teacher(user_id=user.id,name=name,phone=phone,position=position,designation=designation,qualification=qualification,address=address,image_url=image_url)

            db.session.add(teacher)
            db.session.commit()
            flash(f"Teacher '{name}' added successfully!", "success")
            return redirect(url_for('admin_bp.list_teachers'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error adding teacher: {str(e)}", "danger")

    return render_template('admin/add_teacher.html')


@admin_bp.route('/teachers/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_teacher(id):
    teacher = Teacher.query.get_or_404(id)

    if request.method == 'POST':
        try:
            teacher.name = request.form['name']
            teacher.phone = request.form['phone']
            teacher.position = request.form['position']
            teacher.designation = request.form.get('designation')
            teacher.qualification = request.form.get('qualification')
            teacher.address = request.form.get('address')

            # Handle image upload (optional)
            image_file = request.files.get('image')
            if image_file and image_file.filename:
                teacher.image_url = upload_image(image_file)

            teacher.updated_at = datetime.utcnow()
            db.session.commit()

            flash(f"Teacher '{teacher.name}' updated successfully!", "success")
            return redirect(url_for('admin_bp.list_teachers'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating teacher: {str(e)}", "danger")

    return render_template('admin/edit_teacher.html', teacher=teacher)


@admin_bp.route('/teachers/delete/<int:id>', methods=['POST'])
@admin_required
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)

    teacher.position = "0"
    db.session.commit()

    # Disable user login
    user = User.query.get(teacher.user_id)
    if user:
        user.password = str(random.randint(100000, 999999))  # reset password
        db.session.commit()

    flash(f"Teacher '{teacher.name}' has been marked as left.", "info")
    return redirect(url_for('admin_bp.list_teachers'))

from sqlalchemy.orm import joinedload

@admin_bp.route('/teachers/<int:teacher_id>/courses', methods=['GET', 'POST'])
@admin_required
def teacher_courses(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)

    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        if not subject_id:
            flash('Please select a subject to assign.', 'warning')
            return redirect(url_for('admin_bp.teacher_courses', teacher_id=teacher_id))

        subject = Subject.query.get(subject_id)
        if not subject:
            flash('Invalid subject selected.', 'danger')
            return redirect(url_for('admin_bp.teacher_courses', teacher_id=teacher_id))

        class_id = subject.class_id  # link class automatically from subject

        existing = AssignedSubject.query.filter_by(
            teacher_id=teacher.id,
            subject_id=subject.id,
            class_id=class_id
        ).first()

        if existing:
            if existing.status == 'active':
                flash('This course is already assigned to this teacher.', 'info')
            else:
                existing.status = 'active'
                db.session.commit()
                flash(f'{subject.name} re-assigned successfully to {teacher.name}.', 'success')
        else:
            new_assign = AssignedSubject(teacher_id=teacher.id,subject_id=subject.id,class_id=class_id,status='active')
            db.session.add(new_assign)
            db.session.commit()
            flash(f'{subject.name} assigned successfully to {teacher.name}.', 'success')

        return redirect(url_for('admin_bp.teacher_courses', teacher_id=teacher_id))

    # For GET request: load all assigned courses with subject and class
    courses = (
        AssignedSubject.query
        .options(
            joinedload(AssignedSubject.subject),
            joinedload(AssignedSubject.class_)
        )
        .filter_by(teacher_id=teacher.id, status='active').order_by(AssignedSubject.class_id.asc())
        .all()
    )
    # courses = courses.sort()
    # Get all available subjects for dropdown
    subjects = Subject.query.order_by(Subject.name.asc()).all()

    return render_template(
        'admin/assigned_courses.html',
        teacher=teacher,
        courses=courses,
        subjects=subjects
    )


@admin_bp.route('/teachers/<int:teacher_id>/courses/unassign/<int:assign_id>')
@admin_required
def unassign_course(teacher_id, assign_id):
    assign = AssignedSubject.query.get_or_404(assign_id)
    
    if assign.teacher_id != teacher_id:
        flash('Invalid operation.', 'danger')
        return redirect(url_for('admin_bp.teacher_courses', teacher_id=teacher_id))

    # 1️⃣ Set the assignment status inactive
    assign.status = 'inactive'

    # 2️⃣ Delete all routine entries for this teacher and subject
    Routine.query.filter_by(
        teacher_id=teacher_id,
        subject_id=assign.subject_id
    ).delete()

    db.session.commit()
    flash('Course unassigned and routines removed successfully.', 'success')
    return redirect(url_for('admin_bp.teacher_courses', teacher_id=teacher_id))


@admin_bp.route("/teachers/add_rfid/<int:teacher_id>", methods=["POST", "GET"])
@admin_required
def add_teacher_rfid(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    user = User.query.get_or_404(teacher.user_id)
    secret = current_app.config.get("ATTENDANCE_ADD_SECRET")
    items = User.query.filter_by(rfid=secret).all()
    for item in items:
        item.rfid = None
    user.rfid = secret
    db.session.commit()
    flash(f"RFID added successfully to teacher '{teacher.name}'.", "success")
    print(secret)
    us = user.rfid
    print(us)
    return redirect(url_for("admin_bp.list_teachers"))