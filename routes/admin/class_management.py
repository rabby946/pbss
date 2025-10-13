# routes/admin/class_management.py
from flask import render_template, request, redirect, url_for, flash
from . import admin_bp
from models import SchoolClass, Teacher, db
from utils import admin_required
@admin_bp.route("/classes")
@admin_required
def list_classes():
    classes = SchoolClass.query.all()
    return render_template("admin/classes/list.html", classes=classes)

@admin_bp.route("/classes/add", methods=["GET", "POST"])
@admin_required
def add_class():
    if request.method == "POST":
        name = request.form["name"]
        section = request.form["section"]
        teacher_id = request.form.get("teacher_id")

        school_class = SchoolClass(name=name, section=section, teacher_id=teacher_id)
        db.session.add(school_class)
        db.session.commit()
        flash("Class created successfully!", "success")
        return redirect(url_for("admin_bp.list_classes"))

    teachers = Teacher.query.all()
    return render_template("admin/classes/add.html", teachers=teachers)
