# routes/admin/class_management.py
from flask import render_template, request, redirect, url_for, flash
from . import admin_bp
from models import SchoolClass, Teacher, db, Student, Attendance
from utils import admin_required
from datetime import datetime, date


@admin_bp.route('/attendance/<int:student_id>', methods=['GET'])
@admin_required
def attendance(student_id):
    """View attendance for a specific student and date (default: today)."""
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

    # Fetch the single attendance record for the selected date
    attendance_record = (
        Attendance.query
        .filter_by(student_id=student_id)
        .filter(db.func.date(Attendance.created_at) == selected_date)
        .first()
    )

    # Make it consistent for frontend
    attendance_dict = {student.id: attendance_record.status} if attendance_record else {}

    return render_template(
        'admin/attendance.html',
        student=student,
        attendance_dict=attendance_dict,
        selected_date=selected_date,
        today=date.today(), 
        all_attendance_records=[{
        'date': a.created_at.strftime('%Y-%m-%d'),
        'status': a.status
        } for a in Attendance.query.filter_by(student_id=student.id).all()]
    )


@admin_bp.route('/attendance/mark/<int:student_id>', methods=['POST'])
@admin_required
def mark_attendance(student_id):
    """Mark or update attendance for the current date only."""
    student = Student.query.get_or_404(student_id)
    selected_date = date.today()
    status = request.form.get('status')

    if not status:
        flash("No attendance status provided.", "danger")
        return redirect(url_for('admin_bp.attendance', student_id=student_id))

    attendance = (
        Attendance.query
        .filter(Attendance.student_id == student_id)
        .filter(db.func.date(Attendance.created_at) == selected_date)
        .first()
    )

    if attendance:
        attendance.status = status
        attendance.updated_at = datetime.now()
    else:
        attendance = Attendance(
            student_id=student_id,
            status=status,
            created_at=datetime.combine(selected_date, datetime.now().time())
        )
        db.session.add(attendance)

    db.session.commit()
    flash(f"Attendance for {student.name} on {selected_date.strftime('%d %b %Y')} marked as {status}.", "success")
    return redirect(url_for('admin_bp.attendance', student_id=student_id))
