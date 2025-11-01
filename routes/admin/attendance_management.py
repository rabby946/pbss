# routes/admin/class_management.py
from flask import render_template, request, redirect, url_for, flash
from . import admin_bp
from models import SchoolClass, Teacher, db, Student, Attendance, TeacherAttendance
from utils import admin_required
from datetime import datetime, date

@admin_bp.route('/attendance/<int:student_id>', methods=['GET'])
@admin_required
def attendance(student_id):
    date_str = request.args.get('date')
    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    except ValueError:
        flash("Invalid date format.", "danger")
        return redirect(url_for('admin_bp.attendance', student_id=student_id))
    if selected_date > date.today():
        flash("You can't view attendance for future dates.", "warning")
        return redirect(url_for('admin_bp.attendance', student_id=student_id))
    student = Student.query.get_or_404(student_id)
    attendance_record = (Attendance.query.filter_by(student_id=student_id).filter(db.func.date(Attendance.created_at) == selected_date).first())
    attendance_dict = {student.id: attendance_record.status} if attendance_record else {}
    return render_template('admin/attendance.html',student=student,attendance_dict=attendance_dict,selected_date=selected_date,today=date.today(), 
        all_attendance_records=[{
        'date': a.created_at.strftime('%Y-%m-%d'),
        'status': a.status
        } for a in Attendance.query.filter_by(student_id=student.id).all()]
    )

@admin_bp.route('/attendance/mark/<int:student_id>', methods=['POST'])
@admin_required
def mark_attendance(student_id):
    student = Student.query.get_or_404(student_id)
    selected_date = date.today()
    status = request.form.get('status')
    if not status:
        flash("No attendance status provided.", "danger")
        return redirect(url_for('admin_bp.attendance', student_id=student_id))
    attendance = (Attendance.query.filter(Attendance.student_id == student_id).filter(db.func.date(Attendance.created_at) == selected_date).first())
    if attendance:
        attendance.status = status
        attendance.updated_at = datetime.now()
    else:
        attendance = Attendance(student_id=student_id,status=status,created_at=datetime.combine(selected_date, datetime.now().time()))
        db.session.add(attendance)
    db.session.commit()
    flash(f"Attendance for {student.name} on {selected_date.strftime('%d %b %Y')} marked as {status}.", "success")
    return redirect(url_for('admin_bp.attendance', student_id=student_id))

@admin_bp.route('/student-attendances', methods=['GET'])
@admin_required
def student_attendances():
    date_str = request.args.get('date')
    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    except ValueError:
        flash("Invalid date format.", "danger")
        return redirect(url_for('admin_bp.student_attendances'))
    if selected_date > date.today():
        flash("You can't view attendance for future dates.", "warning")
        return redirect(url_for('admin_bp.student_attendances'))
    students = Student.query.order_by(Student.class_id.asc(), Student.name.asc()).all()
    attendances = Attendance.query.filter(db.func.date(Attendance.created_at) == selected_date).all()
    attendance_dict = {a.student_id: a for a in attendances}
    return render_template(
        "admin/studentAttendances.html",
        students=students,
        attendance_dict=attendance_dict,
        selected_date=selected_date,
        today=date.today()
    )


@admin_bp.route('/teacher-attendance/<int:teacher_id>', methods=['GET'])
@admin_required
def teacher_attendance(teacher_id):
    date_str = request.args.get('date')
    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    except ValueError:
        flash("Invalid date format.", "danger")
        return redirect(url_for('admin_bp.teacher_attendance', teacher_id=teacher_id))
    if selected_date > date.today():
        flash("You can't view attendance for future dates.", "warning")
        return redirect(url_for('admin_bp.teacher_attendance', teacher_id=teacher_id))
    teacher = Teacher.query.get_or_404(teacher_id)
    attendance_record = (TeacherAttendance.query.filter_by(teacher_id=teacher_id).filter(db.func.date(TeacherAttendance.date) == selected_date).first())
    attendance_dict = {teacher.id: attendance_record.status} if attendance_record else {}
    all_records = TeacherAttendance.query.filter_by(teacher_id=teacher.id).order_by(TeacherAttendance.date.desc()).all()
    return render_template('admin/teacher_attendance.html',teacher=teacher,attendance_dict=attendance_dict,selected_date=selected_date,today=date.today(),
        all_attendance_records=[{
            'date': a.date.strftime('%Y-%m-%d'),
            'status': a.status,
            'remark': a.remark or ''
        } for a in all_records]
    )
    
@admin_bp.route('/teacher-attendances', methods=['GET'])
@admin_required
def teacher_attendances():
    date_str = request.args.get('date')

    # Parse the selected date safely
    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    except ValueError:
        flash("Invalid date format.", "danger")
        return redirect(url_for('admin_bp.teacher_attendances'))

    # Prevent future date selection
    if selected_date > date.today():
        flash("You can't view attendance for future dates.", "warning")
        return redirect(url_for('admin_bp.teacher_attendances'))
    teachers = Teacher.query.order_by(Teacher.position.asc()).all()
    attendances = TeacherAttendance.query.filter_by(date=selected_date).all()
    attendance_dict = {a.teacher_id: a for a in attendances}
    return render_template(
        "admin/teacherAttendances.html",
        teachers=teachers,
        attendance_dict=attendance_dict,
        selected_date=selected_date,
        today=date.today()
    )

@admin_bp.route('/teacher/<int:teacher_id>/add-leave')
@admin_required
def add_leave(teacher_id):
    date_str = request.args.get('date')
    if date_str:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        selected_date = date.today()
    teacher = Teacher.query.get_or_404(teacher_id)
    attendance = TeacherAttendance.query.filter_by(teacher_id=teacher.id,date=selected_date).first()
    if attendance:
        attendance.status = "Leave"
        attendance.check_in_at = None
        attendance.check_out_at = None
    else:
        attendance = TeacherAttendance(teacher_id=teacher.id,date=selected_date,status="Leave")
        db.session.add(attendance)
    db.session.commit()
    flash(f"{teacher.name} marked as Leave on {selected_date.strftime('%d %b %Y')}", "success")
    return redirect(url_for('admin_bp.teacher_attendances', date=selected_date))
