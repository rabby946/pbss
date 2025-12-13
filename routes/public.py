from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify, current_app
from models import News, Gallery, Teacher, Student, Committee, MPO, Result, Routine, Report, SchoolClass, User, Attendance, TeacherAttendance
from extensions import  db
from datetime import datetime, timedelta
from utils import send_otp_email
from config import Config
from sqlalchemy import func

public_bp = Blueprint("public", __name__)

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


# ---------- Reseting forget password ----------

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
            session.pop('id', None)
            session.pop('reset_otp', None)   
            session.pop('reset_email', None)         
            session.pop('verified_reset', None)
            return redirect(url_for("public.login"))

    return render_template("public/reset_password.html")


@public_bp.route("/attendance/<secret>/<string:rfid>", methods=["GET", "POST"])
def attendance(secret, rfid):
    expected_secret = current_app.config.get("ATTENDANCE_LINK_SECRET")

    if secret != expected_secret:
        return jsonify({
            "status": "failed",
            "received_secret": secret,
            "name" : "N/A",
            "received_message": "Unauthorized secret key"
        })

    user = User.query.filter_by(rfid=rfid).first()

    if user:
        if user.user_type == 'student':
            msg = student_attendance(user.id)
            name = Student.query.filter_by(user_id=user.id).first().name
        else:
            msg = teacher_attendance(user.id)
            name = Teacher.query.filter_by(user_id=user.id).first().name

        return jsonify({
            "status": "success",
            "received_secret": secret,
            "name" : msg,
            "received_message": msg
        })
    add_secret = current_app.config.get("ATTENDANCE_ADD_SECRET")
    users = User.query.filter_by(rfid=add_secret).all()

    if users:
        for u in users:
            u.rfid = None
        users[0].rfid = rfid
        db.session.commit()
        name = users[0].student.name if users[0].user_type == 'student' else users[0].teacher.name
        return jsonify({
            "status": "success",
            "received_secret": secret,
            "name" : name,
            "received_message": "RFID added successfully"
        })
    return jsonify({
        "status": "failed",
        "received_secret": secret,
        "name" : "N/A",
        "received_message": "RFID not recognized"
    })

def student_attendance(user_id):
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return "student not found"
    bd_now = datetime.utcnow() + timedelta(hours=6)
    bd_time = bd_now.time()
    bd_date = bd_now.date()
    attendance = Attendance.query.filter(Attendance.student_id == student.id,func.date(Attendance.created_at) == bd_date).first()
    if attendance:
        if bd_time < datetime.strptime("11:00", "%H:%M").time():
            return f"{student.name}"
        if attendance.check_out_at:
            return f"{student.name}"
        attendance.check_out_at = bd_time
        db.session.commit()
        return f"{student.name}"
    if bd_time < datetime.strptime("11:00", "%H:%M").time():
        status = "present"
    else:
        status = "late"
    attendance = Attendance(student_id=student.id,status=status,check_in_at=bd_time,created_at=bd_now)
    db.session.add(attendance)
    db.session.commit()
    return f"{student.name}"

def teacher_attendance(user_id):
    teacher = Teacher.query.filter_by(user_id=user_id).first()
    if not teacher:
        return "teacher not found"
    bd_now = datetime.utcnow() + timedelta(hours=6)
    bd_time = bd_now.time()
    bd_date = bd_now.date()
    attendance = TeacherAttendance.query.filter(TeacherAttendance.teacher_id == teacher.id,TeacherAttendance.date == bd_date).first()
    if attendance:
        if bd_time < datetime.strptime("11:00", "%H:%M").time():
            return f"{teacher.name}"
        if attendance.check_out_at:
            return f"{teacher.name}"
        attendance.check_out_at = bd_time
        db.session.commit()
        return f"{teacher.name}"
    if bd_time < datetime.strptime("11:00", "%H:%M").time():
        status = "present"
    else:
        status = "late"
    attendance = TeacherAttendance(teacher_id=teacher.id,status=status,check_in_at=bd_time,check_out_at=None,date=bd_date)
    db.session.add(attendance)
    db.session.commit()
    return f"{teacher.name}"