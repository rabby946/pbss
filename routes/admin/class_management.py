# routes/admin/class_management.py
from flask import render_template, request, redirect, url_for, flash
from . import admin_bp
from models import SchoolClass, Teacher, db
from utils import admin_required
from datetime import datetime

@admin_bp.route("/classes", methods=["GET", "POST"])
@admin_required
def list_classes():
    if request.method == "POST":
        action = request.form.get("action")
        name = request.form.get("name")
        section = request.form.get("section")
        teacher_id = request.form.get("teacher_id")
        class_id = request.form.get("class_id")

        if action == "add":
            new_class = SchoolClass(
                name=name,
                section=section,
                teacher_id=teacher_id
            )
            db.session.add(new_class)
            db.session.commit()
            flash("Class created successfully!", "success")
        else:
            flash("Invalid action.", "danger")

    # GET request
    classes = SchoolClass.query.order_by(SchoolClass.id.asc()).all()
    teachers = Teacher.query.filter(Teacher.position != "0").order_by(Teacher.position.asc()).all()
    return render_template("admin/classes.html", classes=classes, teachers=teachers)


@admin_bp.route("/classes/delete/<int:class_id>")
@admin_required
def delete_class(class_id):
    school_class = SchoolClass.query.get(class_id)
    if school_class:
        db.session.delete(school_class)
        db.session.commit()
        flash("Class deleted successfully.", "success")
    else:
        flash("Class not found.", "danger")
    return redirect(url_for("admin_bp.list_classes"))
