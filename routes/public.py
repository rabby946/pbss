from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import News, Gallery, Teacher, Student, Committee, MPO, Result, Routine, Report, User
from flask_mail import Message
from extensions import  db
from datetime import datetime
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
    items = Teacher.query.order_by(Teacher.position.desc()).all()
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
@public_bp.route("/routine")
def routine():
    items = Routine.query.order_by(Routine.id.desc()).all()
    return render_template("public/routine.html",items=items)
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

@public_bp.route("/fix")
def f():
    users_without_email = User.query.filter(User.email.is_(None)).all()
    for user in users_without_email:
        user.email = 'palashbariasecondaryschool@gmail.com'
    db.session.commit()
    print(f"Updated {len(users_without_email)} users with default email.")