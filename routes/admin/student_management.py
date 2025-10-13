# routes/admin/student_management.py
from flask import render_template, request, redirect, url_for, flash
from . import admin_bp
from models import Student, User, db, SchoolClass
from utils import admin_required

@admin_bp.route("/students")
def list_students():
    students = Student.query.all()
    return render_template("admin/students/list.html", students=students)

@admin_bp.route("/students/add", methods=["GET", "POST"])
@admin_required
def add_student():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        class_id = request.form["class_id"]

        user = User(email=email, password=password, user_type="student")
        db.session.add(user)
        db.session.flush()

        student = Student(name=name, user_id=user.id, class_id=class_id)
        db.session.add(student)
        db.session.commit()
        flash("Student added successfully!", "success")
        return redirect(url_for("admin_bp.list_students"))

    classes = SchoolClass.query.all()
    return render_template("admin/students/add.html", classes=classes)
