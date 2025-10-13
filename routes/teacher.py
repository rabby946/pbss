# teacher.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from models import Teacher, Routine, Subject, Student, Attendance, ExamResult, SchoolClass, RegisteredSubject, AssignedSubject, Transaction, News
from utils import teacher_required
from extensions import db
from datetime import datetime, timedelta
from datetime import date 

teacher_bp = Blueprint('teacher_bp', __name__, url_prefix='/teacher')


# ---------- LOGIN ----------
@teacher_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['username']
        password = request.form['password']
        teacher = Teacher.query.filter_by(id=phone).first()
        
        if teacher and teacher.user.password == password:
            session['teacher_id'] = teacher.id
            session['teacher_name'] = teacher.name
            flash('Logged in successfully!', 'success')
            return redirect(url_for('teacher_bp.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('public/login.html')


# ---------- LOGOUT ----------
@teacher_bp.route('/logout')
@teacher_required
def teacher_logout():
    session.pop('teacher_id', None)
    session.pop('teacher_name', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('teacher_bp.login'))


# ---------- DASHBOARD ----------
from datetime import date
from sqlalchemy.orm import joinedload

@teacher_bp.route('/dashboard')
@teacher_required
def dashboard():
    teacher_id = session['teacher_id']

    # Get today's day
    selected_day = date.today().strftime('%A')

    # Query Routine, eagerly load Subject and Subject's class
    routines = (
        Routine.query
        .options(
            joinedload(Routine.subject).joinedload(Subject.class_)
        )
        .filter(Routine.teacher_id == teacher_id, Routine.day == selected_day)
        .order_by(Routine.start_time.asc())
        .all()
    )
    assigned_class = SchoolClass.query.filter_by(teacher_id=teacher_id).first()
    classes = AssignedSubject.query.filter_by(teacher_id=teacher_id, status="active").all()
    countclass = len(classes)
    return render_template('teacher/dashboard.html', routines=routines, assigned_class=assigned_class, classes=classes, countclass=countclass)


@teacher_bp.route("/routine")
@teacher_required
def routine():
    teacher_id = session['teacher_id']
    selected_day = request.args.get('day', 'Monday')
    
    routines = (
        Routine.query
        .join(Subject)
        .filter(Routine.teacher_id == teacher_id, Routine.day == selected_day)
        .order_by(Routine.start_time.asc())
        .all()
    )

    return render_template('teacher/routine.html', teacher = Teacher.query.get_or_404(session["teacher_id"]),routines=routines,selected_day=selected_day)


# ---------- VIEW ATTENDANCE PAGE ----------

@teacher_bp.route('/attendance', methods=['GET', 'POST'])
@teacher_required
def attendance():
    teacher_id = session['teacher_id']
    assigned_class = (
        db.session.query(SchoolClass)
        .join(AssignedSubject, SchoolClass.id == AssignedSubject.class_id)
        .filter(SchoolClass.teacher_id == teacher_id)
        .filter(AssignedSubject.status == "active")
        .first()
    )

    if not assigned_class:
        flash("You are not assigned to any class yet.", "warning")
        return redirect(url_for('teacher_bp.dashboard'))
    class_id = assigned_class.id

    date_str = request.args.get('date')
    if not date_str:
        selected_date = date.today()
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format.", "danger")
            return redirect(url_for('teacher_bp.attendance'))
    else:
        selected_date = date.today()
    if selected_date > date.today():
        flash("You can't submit attendance for future dates.", "danger")
        return redirect(url_for('teacher_bp.attendance'))
    students = (
        db.session.query(Student)
        .join(RegisteredSubject, Student.id == RegisteredSubject.student_id)
        .filter(Student.class_id == class_id)
        .filter(RegisteredSubject.status == "active")
        .distinct()
        .all()
    )
    attendance_records = Attendance.query.filter(
        Attendance.student_id.in_([s.id for s in students]),
        db.func.date(Attendance.created_at) == selected_date).all()
    attendance_dict = {a.student_id: a.status for a in attendance_records}
    return render_template('teacher/attendance.html',students=students,class_id=class_id,selected_date=selected_date,attendance_dict=attendance_dict,today=date.today())

@teacher_bp.route('/attendance/mark', methods=['POST'])
@teacher_required
def mark_attendance():
    teacher_id = session['teacher_id']
    class_id = request.form.get('class_id')
    selected_date = date.today()
    assigned_class = SchoolClass.query.filter_by(id=class_id, teacher_id=teacher_id).first()
    if not assigned_class:
        flash("You are not authorized to mark attendance for this class.", "danger")
        return redirect(url_for('teacher_bp.dashboard'))
    for key, status in request.form.items():
        if key.startswith('student_'):
            student_id = int(key.split("_")[1])
            student = Student.query.filter_by(id=student_id, class_id=class_id).first()
            if not student:
                continue
            attendance = Attendance.query.filter(Attendance.student_id == student_id,db.func.date(Attendance.created_at) == selected_date).first()
            if attendance:
                attendance.status = status
            else:
                attendance = Attendance(student_id=student_id,status=status,created_at=datetime.combine(selected_date, datetime.now().time()))
                db.session.add(attendance)
    db.session.commit()
    flash("Today's attendance marked successfully!", "success")
    return redirect(url_for('teacher_bp.attendance'))


# ---------- TEACHER PROFILE ----------
@teacher_bp.route('/profile', methods=['GET', 'POST'])
@teacher_required
def profile():
    teacher = Teacher.query.get_or_404(session['teacher_id'])

    if request.method == 'POST':
        teacher.name = request.form.get('name')
        teacher.address = request.form.get('address')
        teacher.phone = request.form.get('phone')
        teacher.qualification = request.form.get('qualification')
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for('teacher_bp.profile'))
    return render_template('teacher/profile.html', teacher=teacher)


@teacher_bp.route("/assigned-subjects")
def assigned_subjects():
    teacher_id = session.get("teacher_id")
    if not teacher_id:
        return redirect(url_for("auth.login"))
    assignments = (AssignedSubject.query.filter_by(teacher_id=teacher_id).filter_by(status="active").join(AssignedSubject.subject).join(AssignedSubject.class_).order_by(AssignedSubject.class_id.desc()).all())
    return render_template("teacher/assigned_subjects.html", assignments=assignments)

@teacher_bp.route("/upload-results/<int:subject_id>")
def upload_results(subject_id):
    teacher_id = session.get("teacher_id")
    if not teacher_id:
        return redirect(url_for("auth.login"))
    subject = Subject.query.get_or_404(subject_id)
    registrations = (RegisteredSubject.query.filter_by(subject_id=subject_id, status='active').join(RegisteredSubject.student).order_by(Student.id.desc()).all())
    return render_template("teacher/upload_results.html",subject=subject,registrations=registrations)

from models import ExamResult, db

@teacher_bp.route("/submit-results/<int:subject_id>", methods=["POST"])
def submit_results(subject_id):
    teacher_id = session.get("teacher_id")
    if not teacher_id:
        return redirect(url_for("auth.login"))

    exam_type = request.form.get("exam_type")
    exam_date = request.form.get("exam_date")

    if not exam_type or not exam_date:
        flash("Please select exam type and date.", "warning")
        return redirect(url_for("teacher_bp.upload_results", subject_id=subject_id))

    exam_date_obj = datetime.strptime(exam_date, "%Y-%m-%d")

    def calculate_grade(marks):
        marks = float(marks)
        if marks >= 80: return 5.00
        elif marks >= 70: return 4.00
        elif marks >= 60: return 3.00
        elif marks >= 50: return 2.00
        elif marks >= 40: return 1.00
        else: return 0.00

    for key, value in request.form.items():
        if key.startswith("marks_"):
            student_id = int(key.split("_")[1])
            marks_value = request.form.get(f"marks_{student_id}")
            if not marks_value:
                continue

            marks = float(marks_value)
            grade = calculate_grade(marks)

            existing = ExamResult.query.filter_by(student_id=student_id,subject_id=subject_id,exam_type=exam_type).first()
            if existing:
                # Update existing record
                existing.marks = marks
                existing.grade = grade
                existing.exam_date = exam_date_obj
                existing.updated_at = datetime.utcnow()
            else:
                # Create new record
                result = ExamResult(student_id=student_id,subject_id=subject_id,exam_type=exam_type,marks=marks,grade=grade,exam_date=exam_date_obj,created_at=datetime.utcnow(),updated_at=datetime.utcnow(),)
                db.session.add(result)

    db.session.commit()
    flash("Results saved successfully!", "success")
    return redirect(url_for("teacher_bp.assigned_subjects"))

@teacher_bp.route('/class/students', methods=['GET'])
@teacher_required
def students_list():
    teacher_id = session.get("teacher_id")

    # Find the first class assigned to this teacher
    assigned_class = SchoolClass.query.filter_by(teacher_id=teacher_id).first()
    print(assigned_class)
    if not assigned_class:
        flash("No class assigned to you yet.", "warning")
        return redirect(url_for('teacher_bp.dashboard'))

    # Get all students from that class
    students = Student.query.filter_by(class_id=assigned_class.id).order_by(Student.roll.desc()).all()
    for i in students:
        print(i)
    return render_template(
        'teacher/class_students.html',
        school_class=assigned_class,
        students=students
    )



@teacher_bp.route('/student/<int:student_id>/profile', methods=['GET', 'POST'])
@teacher_required
def student_profile(student_id):
    student = Student.query.get_or_404(student_id)
    transactions = Transaction.query.filter_by(student_id=student.id, status='paid').all()

    # Calculate total payments
    total_paid = sum([float(t.amount) for t in transactions])
    due_amount = float(student.due_amount)

    # Exam clearance decision
    is_cleared = due_amount <= 0

    if request.method == 'POST' and is_cleared:
        flash(f"Exam clearance (probesh potro) issued for {student.name} ✅", "success")
        
    elif request.method == 'POST' and not is_cleared:
        flash(f"{student.name} has due amount ${due_amount:.2f}. Clearance denied.", "danger")

    return render_template(
        'teacher/student_profile.html',
        student=student,
        transactions=transactions,
        total_paid=total_paid,
        is_cleared=is_cleared
    )

@teacher_bp.route('/news', methods=['GET'])
@teacher_required
def view_news():
    all_news = News.query.order_by(News.timestamp.desc()).all()
    return render_template('teacher/news_list.html', news_list=all_news)


@teacher_bp.route('/news/add', methods=['GET', 'POST'])
@teacher_required
def add_news():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        new_entry = News(title=title, description=description)
        db.session.add(new_entry)
        db.session.commit()
        flash("📰 News added successfully!", "success")
        return redirect(url_for('teacher_bp.view_news'))

    return render_template('teacher/add_news.html')


@teacher_bp.route('/news/delete/<int:news_id>', methods=['POST'])
@teacher_required
def delete_news(news_id):
    news = News.query.get_or_404(news_id)
    db.session.delete(news)
    db.session.commit()
    flash("🗑️ News deleted successfully!", "success")
    return redirect(url_for('teacher_bp.view_news'))
