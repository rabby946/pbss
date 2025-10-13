from flask import render_template, session, redirect, url_for, flash, redirect, request, current_app
from . import admin_bp
from utils import admin_required  
from models import Teacher, Student, SchoolClass, Subject

@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    teacher_count = Teacher.query.count()
    student_count = Student.query.count()
    class_count = SchoolClass.query.count()
    subject_count = Subject.query.count()

    return render_template(
        "admin/dashboard.html",
        teacher_count=teacher_count,
        student_count=student_count,
        class_count=class_count,
        subject_count=subject_count,
    )
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin"):
        flash("Already logged in.", "warning")
        return redirect(url_for("admin_bp.dashboard"))

    if request.method == "POST":
        entered_password = request.form.get("password", "").strip()
        admin_password = current_app.config.get("ADMIN_PASSWORD")
        if entered_password == admin_password:
            session["admin"] = True
            flash("Logged in successfully! ✔️", "success")
            return redirect(url_for("admin_bp.dashboard"))
        flash("Invalid password ❌", "error")

    return render_template("admin/login.html")


@admin_bp.route("/logout")
@admin_required
def logout():
    session["admin"] = False
    flash("Logged out successfully ✔️", "success")
    return redirect(url_for("admin_bp.login"))


