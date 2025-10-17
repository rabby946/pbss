from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import News, Gallery, Teacher, Student, Committee, MPO, Result, Routine, Report, User
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
    return render_template("public/entity.html",entity_items=items,entity_name="Teachers",detail_endpoint="public.teacher_detail")

@public_bp.route("/teacher/<int:id>")
def teacher_detail(id):
    item = Teacher.query.get_or_404(id)
    return render_template("public/entity_detail.html",item=item,description=item.position, endpoint="public.teachers")


# ---------- Students ----------
@public_bp.route("/students")
def students():
    items = Student.query.order_by(Student.id.desc()).all()
    return render_template("public/entity.html",entity_items=items,entity_name="Students",detail_endpoint="public.student_detail")

@public_bp.route("/student/<int:id>")
def student_detail(id):
    item = Student.query.get_or_404(id)
    return render_template("public/entity_detail.html",item=item,description=item.roll, endpoint="public.students")
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

    return render_template(
        "public/routine.html",
        routines=routines,
        days=days,
        classes=classes,
        teachers=teachers,
        subjects=subjects,
        selected_day=selected_day,
        selected_class=selected_class,
        selected_teacher=selected_teacher,
        selected_subject=selected_subject
    )

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

@public_bp.route("/forgot_password")
def forgot_password():
    return render_template("public/forgot_password.html")
from datetime import datetime, time
@public_bp.route("/fix")
@admin_required
def fix_subjects():
    return f"✅ Deleted invalid subjects (with NULL class_id or teacher_id)"
