from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from datetime import datetime
from werkzeug.security import check_password_hash
from models import db, Student, User, ExamResult, Attendance, RegisteredSubject, Subject, Transaction, Routine, News, Teacher
from extensions import db
from utils import student_required, upload_image
from calendar import monthrange
    
student_bp = Blueprint('student_bp', __name__, url_prefix='/student')


@student_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        studentID = request.form.get('nid')
        password = request.form.get('password')
        student = Student.query.filter_by(studentID=studentID).first()
        if not student:
            flash("Student not found.", "danger")
            return redirect(url_for('public.login'))
        user = User.query.get(student.user_id)
        if user and user.password == password:
            session['student_id'] = student.id
            session['student_name'] = student.name
            flash("Login successful!", "success")
            return redirect(url_for('student_bp.dashboard'))
        flash("Invalid credentials.", "danger")
    return render_template('public/login.html')


@student_bp.route('/logout')
def student_logout():
    session.pop('student_id', None)
    session.pop('student_name', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('public.login'))


@student_bp.route('/dashboard')
@student_required
def dashboard():
    student = Student.query.get(session['student_id'])
    recent_news = News.query.order_by(News.timestamp.desc()).limit(5).all()
    results_count = ExamResult.query.filter_by(student_id=student.id).count()
    attendance_count = Attendance.query.filter_by(student_id=student.id).count()
    return render_template('student/dashboard.html',student=student,notices=recent_news,results_count=results_count,attendance_count=attendance_count)


@student_bp.route('/profile', methods=['GET', 'POST'])
@student_required
def profile():
    student = Student.query.get_or_404(session['student_id'])
    user = student.user  
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        address = request.form.get('address', '').strip()
        blood_group = request.form.get('blood_group', '').strip()
        image_file = request.files.get('image')
        student.name = name
        student.address = address
        student.blood_group = blood_group
        if image_file and image_file.filename:
            student.image_url = upload_image(image_file)
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for('student_bp.profile'))
    return render_template('student/profile.html', student=student, user=user)

@student_bp.route('/results', methods=['GET'])
@student_required
def results():
    student_id = session['student_id']
    subject_filter = request.args.get('subject')
    query = ExamResult.query.filter_by(student_id=student_id)
    if subject_filter:
        query = query.join(Subject).filter(Subject.name.ilike(f"%{subject_filter}%"))
    results = query.join(Subject, ExamResult.subject_id == Subject.id) \
                   .add_columns(Subject.name.label('subject_name'), ExamResult.exam_type,
                                ExamResult.marks, ExamResult.grade, ExamResult.exam_date) \
                   .order_by(ExamResult.created_at.desc()).all()
    return render_template('student/results.html', results=results, subject_filter=subject_filter)

@student_bp.route('/payments', methods=['GET', 'POST'])
@student_required
def payments():
    student_id = session['student_id']
    if request.method == 'POST':
        amount = request.form.get('amount')
        payment_method = request.form.get('payment_method')
        txn = Transaction(student_id=student_id, amount=amount, payment_method=payment_method, status='pending')
        db.session.add(txn)
        Student.query(id=student_id).due_amount -= amount
        db.session.commit()
        flash("Payment request submitted.", "success")
        return redirect(url_for('student_bp.payments'))
    transactions = Transaction.query.filter_by(student_id=student_id).order_by(Transaction.created_at.desc()).all()
    return render_template('student/payments.html', transactions=transactions)


@student_bp.route('/routines', methods=['GET'])
@student_required
def routines():
    student = Student.query.get_or_404(session['student_id'])
    selected_day = request.args.get('day', 'Monday')
    if not student.class_id:
        flash("You are not assigned to any class yet.", "warning")
        return render_template('student/routine.html', routines=[], selected_day=selected_day, student=student)
    routines = (Routine.query.join(Subject).join(Teacher).filter(Routine.day == selected_day).filter(Subject.class_id == student.class_id).order_by(Routine.start_time.asc()).add_entity(Subject).add_entity(Teacher).all())
    return render_template('student/routines.html',routines=routines,selected_day=selected_day,student=student)

@student_bp.route('/notices')
@student_required
def notices():
    news = News.query.order_by(News.timestamp.desc()).all()
    return render_template('student/notices.html', news=news)

@student_bp.route('/attendance', methods=['GET', 'POST'])
@student_required
def attendance():
    student_id = session['student_id']
    records = Attendance.query.filter_by(student_id=student_id).all()

    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    attendance_map = {}
    for rec in records:
        if rec.created_at.year == year and rec.created_at.month == month:
            day = rec.created_at.day
            attendance_map[day] = {
                'status': rec.status,
                'check_in_at': rec.check_in_at.strftime("%I:%M %p") if rec.check_in_at else "-",
                'check_out_at': rec.check_out_at.strftime("%I:%M %p") if rec.check_out_at else "-"
            }

    # Generate all days in the month
    num_days = monthrange(year, month)[1]
    days = []
    for day in range(1, num_days + 1):
        date_obj = datetime(year, month, day)
        weekday_name = date_obj.strftime("%a")  # Mon, Tue, etc.
        rec = attendance_map.get(day, None)
        days.append({'day': day,'weekday': weekday_name,'status': rec['status'] if rec else 'none','check_in_at': rec['check_in_at'] if rec else '-','check_out_at': rec['check_out_at'] if rec else '-'})

    stats = {
        "present": sum(1 for d in days if d['status'] == "present"),
        "absent": sum(1 for d in days if d['status'] == "absent"),
        "late": sum(1 for d in days if d['status'] == "late"),
    }
    stats["percentage"] = round(((stats["present"] + stats["late"]) / num_days) * 100, 1)

    return render_template('student/attendance.html',year=year,month=month,days=days,stats=stats)