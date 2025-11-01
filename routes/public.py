from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import News, Gallery, Teacher, Student, Committee, MPO, Result, Routine, Report, SchoolClass, User
from flask_mail import Message
from extensions import  db
from datetime import datetime
public_bp = Blueprint("public", __name__)
from utils import admin_required
@public_bp.context_processor
def inject_year():
    return {'moment': datetime.now().year} 

# ---------- Home ----------
@public_bp.route("/")
def home():
    headline_item = News.query.order_by(News.id.desc()).first()
    headline = headline_item.title if headline_item else "No news yet"
    headline2 = headline_item.description if headline_item else ""
    notice = notice = News.query.order_by(News.id.desc()).limit(3)
    return render_template("public/home.html", text=headline, text2=headline2, notice=notice)

# ---------- News ----------
@public_bp.route("/news")
def news():
    items = News.query.order_by(News.id.desc()).all()
    return render_template( "public/news.html",news_items=items)

@public_bp.route("/news/<int:id>")
def news_detail(id):
    news_item = News.query.get_or_404(id)
    return render_template("public/news_detail.html", item=news_item)

# ---------- Gallery ----------
@public_bp.route("/gallery")
def gallery():
    items = Gallery.query.order_by(Gallery.id.desc()).all()
    return render_template("public/gallery.html", items=items)

@public_bp.route("/gallery/<int:id>")
def gallery_detail(id):
    item = Gallery.query.get_or_404(id)
    # Convert comma-separated string into list
    item.images = item.images.split(",") if item.images else []
    return render_template("public/gallery_detail.html", item=item)

# ---------- Teachers ----------
@public_bp.route("/teachers")
def teachers():
    items = Teacher.query.filter(Teacher.position != "0").order_by(Teacher.position.asc()).all()
    return render_template("public/teachers.html",items=items)

@public_bp.route("/teacher/<int:id>")
def teacher_detail(id):
    item = Teacher.query.get_or_404(id)
    return render_template("public/teacher_detail.html",item=item)


# ---------- Students ----------
@public_bp.route("/students")
def students():
    selected_class = request.args.get("class_id", "all")
    query = Student.query.order_by(Student.id.desc())
    if selected_class != "all":
        query = query.filter(Student.class_id == int(selected_class))
    items = query.all()  # Execute after filtering
    classes = SchoolClass.query.order_by(SchoolClass.id.asc()).all()
    return render_template("public/students.html", items=items, classes=classes)

@public_bp.route("/student/<int:id>")
def student_detail(id):
    item = Student.query.get_or_404(id)
    return render_template("public/student_detail.html",item=item)

# ---------- Committee ----------
@public_bp.route("/committees")
def committees():
    items = Committee.query.order_by(Committee.id.desc()).all()
    return render_template("public/entity.html",entity_items=items,entity_name="Committee",detail_endpoint="public.committee_detail")
@public_bp.route("/committee/<int:id>")
def committee_detail(id):
    item = Committee.query.get_or_404(id)
    return render_template("public/entity_detail.html",item=item,description=item.designation, endpoint="public.committees")
# ---------- MPO ----------
@public_bp.route("/mpos")
def mpos():
    items = MPO.query.order_by(MPO.id.desc()).all()
    return render_template("public/entity.html",entity_items=items,entity_name="Accreditations",detail_endpoint="public.mpo_detail")

@public_bp.route("/mpo/<int:id>")
def mpo_detail(id):
    item = MPO.query.get_or_404(id)
    return render_template("public/entity_detail.html",item=item,description=item.designation, endpoint="public.mpos")
# ---------- Results ----------
@public_bp.route("/results")
def results():
    items = Result.query.order_by(Result.id.desc()).all()
    return render_template("public/results.html", items=items)
# ---------- Routine ----------

from models import Routine, Subject, Teacher, SchoolClass

@public_bp.route("/routine", methods=["GET"])
def routine():
    # Get filters from query parameters
    selected_day = request.args.get("day", "all")
    selected_class = request.args.get("class_id", "all")
    selected_teacher = request.args.get("teacher_id", "all")
    selected_subject = request.args.get("subject_id", "all")

    # Base query with joins for optimization
    query = db.session.query(Routine)\
        .join(Subject, Routine.subject_id == Subject.id)\
        .join(Teacher, Routine.teacher_id == Teacher.id)\
        .join(SchoolClass, Subject.class_id == SchoolClass.id)

    # Apply filters
    if selected_day != "all":
        query = query.filter(Routine.day == selected_day)
    if selected_class != "all":
        query = query.filter(SchoolClass.id == int(selected_class))
    if selected_teacher != "all":
        query = query.filter(Teacher.id == int(selected_teacher))
    if selected_subject != "all":
        query = query.filter(Subject.id == int(selected_subject))

    routines = query.order_by(Routine.day, Routine.start_time).all()

    # Dropdown data
    days = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    classes = SchoolClass.query.order_by(SchoolClass.id).all()
    teachers = Teacher.query.order_by(Teacher.position).all()
    subjects = Subject.query.order_by(Subject.class_id).all()

    return render_template("public/routine.html",routines=routines,days=days,classes=classes,teachers=teachers,subjects=subjects,selected_day=selected_day,selected_class=selected_class,selected_teacher=selected_teacher,selected_subject=selected_subject)

# ---------- Contact ----------
@public_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        purpose = request.form.get("subject")
        message = request.form.get("message")
        report = Report(name=name, email=email, purpose=purpose, message=message)
        db.session.add(report)
        db.session.commit()
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return {"success": True}
        flash("posted your issue")
        return redirect(url_for("public.contact"))

    return render_template("public/contact.html")

@public_bp.route("/login")
def login():
    return render_template("public/login.html")

from utils import send_otp_email
from flask import session

@public_bp.route("/forgot_password", methods = ["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        user_type = request.form.get("userType")
        if user_type == "student":
            student_id = request.form.get("studentID")
            student = Student.query.get_or_404(student_id)
            if student and student.user.email:
                send_otp_email(student.user.email, student.name)
                session['id'] = student.user.id
                flash(f"OTP sent to your registered email address : {student.user.email}.", "success")
                return redirect(url_for("public.verify_otp"))
            else:
                flash("Student not found or phone number not added!", "danger")
        elif user_type == "teacher":
            teacher_id = request.form.get("teacher_id")
            teacher = Teacher.get_or_404(teacher_id)
            if teacher and teacher.user.email:
                send_otp_email(teacher.user.email, teacher.name)
                session['id'] = teacher.user.id
                flash(f"OTP sent to your registered eamil address : {teacher.user.email}.", "success")
                return redirect(url_for("public.verify_otp"))
            else:
                flash(f"Teacher not found or phone number not added", "danger")
        else:
            flash("error type selection", "danger")
    students = Student.query.all()
    teachers = Teacher.query.all()
    return render_template("public/forgot_password.html", students = students, teachers = teachers)


@public_bp.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        otp_input = request.form.get("otp")
        if otp_input == session.get("reset_otp"):
            session['verified_reset'] = True
            flash("OTP verified! You can reset your password now.", "success")
            return redirect(url_for("public.reset_password"))
        else:
            flash("Invalid OTP.", "danger")
    return render_template("public/verify_otp.html")

@public_bp.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if not session.get('verified_reset'):
        return redirect(url_for("public.forgot_password"))
    if request.method == "POST":
        new_pass = request.form.get("new_password") 
        obj = User.query.filter_by(id=session['id']).first()
        if obj:
            obj.password = new_pass  # Ideally hash this later
            db.session.commit()
            flash("Password reset successfully!", "success")
            # Clear session data
            session.pop('id', None)
            session.pop('reset_otp', None)   
            session.pop('reset_email', None)         
            session.pop('verified_reset', None)
            return redirect(url_for("public.login"))

    return render_template("public/reset_password.html")

import random
from datetime import date, timedelta, datetime
from flask import jsonify
from models import Teacher, TeacherAttendance
from extensions import db

@public_bp.route("/fix")
@admin_required
def fix_subjects():
    """Generate random attendance data for teachers for testing."""
    teachers = Teacher.query.all()
    if not teachers:
        return jsonify({"message": "No teachers found in the database."}), 404

    # Define how many days to generate (today + last 3 days)
    days_back = 3
    today_date = date.today()

    statuses = ["Present", "Absent", "Leave"]

    added = 0
    for i in range(days_back + 1):  # includes today
        day = today_date - timedelta(days=i)
        for teacher in teachers:
            # Check if already exists to avoid duplicates
            existing = TeacherAttendance.query.filter(
                TeacherAttendance.teacher_id == teacher.id,
                db.func.date(TeacherAttendance.date) == day
            ).first()

            if not existing:
                status = random.choice(statuses)
                remark = ""
                if status == "Absent":
                    remark = random.choice(["Sick leave", "Family emergency", "Uninformed absence", ""])
                elif status == "Leave":
                    remark = random.choice(["Official leave", "Training", "Personal reason", ""])
                else:
                    remark = random.choice(["On time", "Late arrival", ""])

                attendance = TeacherAttendance(
                    teacher_id=teacher.id,
                    date=day,
                    status=status,
                    remark=remark,
                    created_at=datetime.combine(day, datetime.now().time())
                )
                db.session.add(attendance)
                added += 1

    db.session.commit()
    return jsonify({
        "message": f"✅ Added {added} random attendance records for {len(teachers)} teachers over last {days_back + 1} days.",
        "dates": [str(today_date - timedelta(days=i)) for i in range(days_back + 1)]
    })

