from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import cloudinary.uploader
import json
from functools import wraps
from models import db, News, Gallery, Teacher, Student, Committee, MPO, Result, Routine
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from models import db, Teacher, Student, MPO, Committee, Result, Routine, News, Gallery, Report
import os
from utils import admin_required, upload_to_imgbb

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# ----------------------
# Admin Authentication
# ----------------------


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin"):
        flash("Already logged in.", "warning")
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        entered_password = request.form.get("password", "").strip()
        admin_password = current_app.config.get("ADMIN_PASSWORD")
        if entered_password == admin_password:
            session["admin"] = True
            flash("Logged in successfully! ✔️", "success")
            return redirect(url_for("admin.dashboard"))
        flash("Invalid password ❌", "error")

    return render_template("admin/login.html")


@admin_bp.route("/logout")
@admin_required
def logout():
    session["admin"] = False
    flash("Logged out successfully ✔️", "success")
    return redirect(url_for("admin.login"))

@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    return render_template("admin/dashboard.html")


# Make sure you have this folder structure
UPLOAD_FOLDER_IMAGES = "static/images"
UPLOAD_FOLDER_PDFS = "static/pdfs"

@admin_bp.route("/reports")
@admin_required
def reports():
    items = Report.query.order_by(Report.id.desc()).all()
    return render_template("admin/reports.html", items=items)

@admin_bp.route('/delete-report/<int:id>', methods=['POST']) 
@admin_required 
def delete_reports(id):
    if request.method == 'POST':
        report_to_delete = Report.query.get_or_404(id)
        db.session.delete(report_to_delete)
        db.session.commit()
        flash('Report has been deleted successfully.', 'success')
        return redirect(url_for('admin.reports')) 
    return redirect(url_for('admin.reports'))

@admin_bp.route("/admin/more_about/<int:id>")
@admin_required
def more_about(id):
    item = Report.query.get_or_404(id)
    return render_template("admin/more_about.html", item=item)

# ------------------ TEACHERS ------------------ #

@admin_bp.route("/teachers")
@admin_required
def teachers():
    items = Teacher.query.order_by(Teacher.id.desc()).all()
    return render_template("admin/teachers.html", items=items)

@admin_bp.route("/teachers/add", methods=["GET", "POST"])
@admin_required
def add_teacher():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("position")
        file = request.files.get("filename")

        image_url = None
        if "photo" in request.files:
            file = request.files["photo"]
            if file.filename:
                image_url = upload_to_imgbb(file)

        teacher = Teacher(name=name, position=description, image_url=image_url)
        db.session.add(teacher)
        db.session.commit()
        flash("Teacher added successfully!", "success")
        return redirect(url_for("admin.teachers"))

    return render_template("admin/add_teacher.html")

@admin_bp.route("/teachers/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    if request.method == "POST":
        teacher.name = request.form.get("name")
        teacher.position = request.form.get("description")
        file = request.files.get("photo")
        image_url = None
        if "photo" in request.files:
            file = request.files["photo"]
            if file.filename:
                image_url = upload_to_imgbb(file)
                teacher.image_url = image_url
        db.session.commit()
        flash("Teacher updated successfully!", "success")
        return redirect(url_for("admin.teachers"))
    return render_template("admin/edit_teacher.html", item=teacher)

@admin_bp.route("/teachers/delete/<int:id>")
@admin_required
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    db.session.delete(teacher)
    db.session.commit()
    flash("Teacher deleted successfully!", "success")
    return redirect(url_for("admin.teachers"))
@admin_bp.route("/teachers/swap/<int:id1>/<int:id2>")
@admin_required
def teacher_swap_between(id1, id2):
    item1 = Teacher.query.get_or_404(id1)
    item2 = Teacher.query.get_or_404(id2)

    item1.name, item2.name = item2.name, item1.name
    item1.position, item2.position = item2.position, item1.position
    item1.image_url, item2.image_url = item2.image_url, item1.image_url
    item1.timestamp, item2.timestamp = item2.timestamp, item1.timestamp
    db.session.commit()
    flash("swapped successfully", "success")
    return redirect(url_for("admin.teacher_swap"))

@admin_bp.route("/teachers/swap")
@admin_required
def teacher_swap():
    items = Teacher.query.order_by(Teacher.id.desc()).all()
    return render_template("admin/teachers_swap.html", items=items)


# ------------------ STUDENTS ------------------ #
@admin_bp.route("/students")
@admin_required
def students():
    items = Student.query.order_by(Student.id.desc()).all()
    return render_template("admin/students.html", items=items)

@admin_bp.route("/students/add", methods=["GET", "POST"])
@admin_required
def add_student():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("roll")
        file = request.files.get("photo")
        image_url = None
        if "photo" in request.files:
            file = request.files["photo"]
            if file.filename:
                image_url = upload_to_imgbb(file)

        student = Student(name=name, roll=description, image_url=image_url)
        db.session.add(student)
        db.session.commit()
        flash("Student added successfully!", "success")
        return redirect(url_for("admin.students"))

    return render_template("admin/add_student.html")

@admin_bp.route("/students/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    if request.method == "POST":
        student.name = request.form.get("name")
        student.roll = request.form.get("description")
        file = request.files.get("photo")
        image_url = None
        if "photo" in request.files:
            file = request.files["photo"]
            if file.filename:
                image_url = upload_to_imgbb(file)
                student.image_url = image_url
        db.session.commit()
        flash("Student updated successfully!", "success")
        return redirect(url_for("admin.students"))

    return render_template("admin/edit_student.html", item=student)

@admin_bp.route("/students/delete/<int:id>")
@admin_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash("Student deleted successfully!", "success")
    return redirect(url_for("admin.students"))

@admin_bp.route("/students/swap/<int:id1>/<int:id2>")
@admin_required
def student_swap_between(id1, id2):
    item1 = Student.query.get_or_404(id1)
    item2 = Student.query.get_or_404(id2)

    item1.name, item2.name = item2.name, item1.name
    item1.roll, item2.roll = item2.roll, item1.roll
    item1.image_url, item2.image_url = item2.image_url, item1.image_url
    item1.timestamp, item2.timestamp = item2.timestamp, item1.timestamp
    db.session.commit()
    flash("swapped successfully", "success")
    return redirect(url_for("admin.student_swap"))

@admin_bp.route("/students/swap")
@admin_required
def student_swap():
    items = Student.query.order_by(Student.id.desc()).all()
    return render_template("admin/students_swap.html", items=items)


# ------------------ MPOs ------------------ #
@admin_bp.route("/mpos")
@admin_required
def mpos():
    items = MPO.query.order_by(MPO.id.desc()).all()
    return render_template("admin/mpos.html", items=items)

@admin_bp.route("/mpos/add", methods=["GET", "POST"])
@admin_required
def add_mpo():
    if request.method == "POST":
        name = request.form.get("name")
        designation = request.form.get("description")
        file = request.files.get("filename")
        image_url = None
        if "filename" in request.files:
            file = request.files["filename"]
            if file.filename:
                image_url = upload_to_imgbb(file)

        mpo = MPO(name=name, designation=designation, image_url=image_url)
        db.session.add(mpo)
        db.session.commit()
        flash("MPO added successfully!", "success")
        return redirect(url_for("admin.mpos"))

    return render_template("admin/add_mpo.html")

@admin_bp.route("/mpos/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_mpo(id):
    mpo = MPO.query.get_or_404(id)
    if request.method == "POST":
        mpo.name = request.form.get("name")
        mpo.designation = request.form.get("description")
        image_url = None
        if "filename" in request.files:
            file = request.files["filename"]
            if file.filename:
                image_url = upload_to_imgbb(file)
                mpo.image_url = image_url

        db.session.commit()
        flash("MPO updated successfully!", "success")
        return redirect(url_for("admin.mpos"))

    return render_template("admin/edit_mpo.html", item=mpo)

@admin_bp.route("/mpos/delete/<int:id>")
@admin_required
def delete_mpo(id):
    mpo = MPO.query.get_or_404(id)
    db.session.delete(mpo)
    db.session.commit()
    flash("MPO deleted successfully!", "success")
    return redirect(url_for("admin.mpos"))
@admin_bp.route("/mpos/swap/<int:id1>/<int:id2>")
@admin_required
def mpo_swap_between(id1, id2):
    item1 = MPO.query.get_or_404(id1)
    item2 = MPO.query.get_or_404(id2)

    item1.name, item2.name = item2.name, item1.name
    item1.designation, item2.designation = item2.designation, item1.designation
    item1.image_url, item2.image_url = item2.image_url, item1.image_url
    item1.timestamp, item2.timestamp = item2.timestamp, item1.timestamp
    db.session.commit()
    flash("swapped successfully", "success")
    return redirect(url_for("admin.mpo_swap"))

@admin_bp.route("/mpos/swap")
@admin_required
def mpo_swap():
    items = MPO.query.order_by(MPO.id.desc()).all()
    return render_template("admin/mpos_swap.html", items=items)


# ------------------ COMMITTEES ------------------ #
@admin_bp.route("/committees")
@admin_required
def committees():
    items = Committee.query.order_by(Committee.id.desc()).all()
    return render_template("admin/committees.html", items=items)

@admin_bp.route("/committees/add", methods=["GET", "POST"])
@admin_required
def add_committee():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("position")
        image_url = None
        if "filename" in request.files:
            file = request.files["filename"]
            if file.filename:
                image_url = upload_to_imgbb(file)
        committee = Committee(name=name, designation=description, image_url=image_url)
        db.session.add(committee)
        db.session.commit()
        flash("Committee added successfully!", "success")
        return redirect(url_for("admin.committees"))

    return render_template("admin/add_committee.html")

@admin_bp.route("/committees/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_committee(id):
    committee = Committee.query.get_or_404(id)
    if request.method == "POST":
        committee.name = request.form.get("name")
        committee.designation = request.form.get("description")

        image_url = None
        if "filename" in request.files:
            file = request.files["filename"]
            if file.filename:
                image_url = upload_to_imgbb(file)
                committee.image_url = image_url

        db.session.commit()
        flash("Committee updated successfully!", "success")
        return redirect(url_for("admin.committees"))

    return render_template("admin/edit_committee.html", item=committee)

@admin_bp.route("/committees/delete/<int:id>")
@admin_required
def delete_committee(id):
    committee = Committee.query.get_or_404(id)
    db.session.delete(committee)
    db.session.commit()
    flash("Committee deleted successfully!", "success")
    return redirect(url_for("admin.committees"))

@admin_bp.route("/committees/swap/<int:id1>/<int:id2>")
@admin_required
def committee_swap_between(id1, id2):
    item1 = Committee.query.get_or_404(id1)
    item2 = Committee.query.get_or_404(id2)

    item1.name, item2.name = item2.name, item1.name
    item1.designation, item2.designation = item2.designation, item1.designation
    item1.image_url, item2.image_url = item2.image_url, item1.image_url
    item1.timestamp, item2.timestamp = item2.timestamp, item1.timestamp
    db.session.commit()
    flash("swapped successfully", "success")
    return redirect(url_for("admin.committee_swap"))

@admin_bp.route("/committees/swap")
@admin_required
def committee_swap():
    items = Committee.query.order_by(Committee.id.desc()).all()
    return render_template("admin/committees_swap.html", items=items)


# ------------------ RESULTS ------------------ #

@admin_bp.route("/results")
@admin_required
def results():   
    items = Result.query.order_by(Result.id.desc()).all()
    return render_template("admin/results.html", items=items)


@admin_bp.route("/results/add", methods=["GET", "POST"])
@admin_required
def add_result():
    if request.method == "POST":
        title = request.form.get("title")
        file = request.files.get("file")
        if not file:
            flash("No file uploaded!", "danger")
            return redirect(url_for("admin.add_result"))
        upload_result = cloudinary.uploader.upload(file,resource_type="raw")
        pdf_url = upload_result["secure_url"]
        result = Result(title=title, file_url=pdf_url)
        db.session.add(result)
        db.session.commit()
        flash("Result added successfully!", "success")
        return redirect(url_for("admin.results"))
    return render_template("admin/add_result.html")

@admin_bp.route("/results/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_result(id):
    result = Result.query.get_or_404(id)
    if request.method == "POST":
        result.title = request.form.get("title")
        file = request.files.get("file")
        if not file:
            flash("File remains same !", "danger")
        else:
            upload_result = cloudinary.uploader.upload(file,resource_type="raw")
            result.file_url = upload_result["secure_url"]
        db.session.commit()
        flash("Result updated successfully!", "success")
        return redirect(url_for("admin.results"))
    return render_template("admin/edit_result.html", item=result)

@admin_bp.route("/results/delete/<int:id>")
@admin_required
def delete_result(id):
    result = Result.query.get_or_404(id)
    db.session.delete(result)
    db.session.commit()
    flash("Result deleted successfully!", "success")
    return redirect(url_for("admin.results"))

@admin_bp.route("/result/swap/<int:id1>/<int:id2>")
@admin_required
def result_swap_between(id1, id2):
    item1 = Result.query.get_or_404(id1)
    item2 = Result.query.get_or_404(id2)

    item1.title, item2.title = item2.title, item1.title
    item1.file_url, item2.file_url = item2.file_url, item1.file_url
    item1.timestamp, item2.timestamp = item2.timestamp, item1.timestamp
    db.session.commit()
    flash("swapped successfully", "success")
    return redirect(url_for("admin.result_swap"))

@admin_bp.route("/result/swap")
@admin_required
def result_swap():
    items = Result.query.order_by(Result.id.desc()).all()
    return render_template("admin/result_swap.html", items=items)



# ------------------ ROUTINES ------------------ #
@admin_bp.route("/routines")
@admin_required
def routines():
    items = Routine.query.order_by(Routine.id.desc()).all()
    return render_template("admin/routines.html", items=items)

@admin_bp.route("/routines/add", methods=["GET", "POST"])
@admin_required
def add_routine():
    if request.method == "POST":
        title = request.form.get("title")
        file = request.files.get("file")
        if not file:
            flash("No file uploaded!", "danger")
            return redirect(url_for("admin.add_routine"))
        upload_result = cloudinary.uploader.upload(file, resource_type="raw")
        pdf_url = upload_result["secure_url"]
        routine = Routine(title=title, file_url=pdf_url)
        db.session.add(routine)
        db.session.commit()
        flash("Routine added successfully!", "success")
        return redirect(url_for("admin.routines"))
    return render_template("admin/add_routine.html")

@admin_bp.route("/routines/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_routine(id):
    routine = Routine.query.get_or_404(id)
    if request.method == "POST":
        routine.title = request.form.get("title")
        file = request.files.get("file")
        if file:
            upload_result = cloudinary.uploader.upload(file, resource_type="raw")
            routine.file_url = upload_result["secure_url"]
        db.session.commit()
        flash("Routine updated successfully!", "success")
        return redirect(url_for("admin.routines"))

    return render_template("admin/edit_routine.html", item=routine)

@admin_bp.route("/routines/delete/<int:id>")
@admin_required
def delete_routine(id):
    routine = Routine.query.get_or_404(id)
    db.session.delete(routine)
    db.session.commit()
    flash("Routine deleted successfully!", "success")
    return redirect(url_for("admin.routines"))
@admin_bp.route("/routine/swap/<int:id1>/<int:id2>")
@admin_required
def routine_swap_between(id1, id2):
    item1 = Routine.query.get_or_404(id1)
    item2 = Routine.query.get_or_404(id2)

    item1.title, item2.title = item2.title, item1.title
    item1.file_url, item2.file_url = item2.file_url, item1.file_url
    item1.timestamp, item2.timestamp = item2.timestamp, item1.timestamp
    db.session.commit()
    flash("swapped successfully", "success")
    return redirect(url_for("admin.routine_swap"))

@admin_bp.route("/routine/swap")
@admin_required
def routine_swap():
    items = Routine.query.order_by(Routine.id.desc()).all()
    return render_template("admin/routine_swap.html", items=items)

# ------------------ NEWS ------------------ #
@admin_bp.route("/news")
@admin_required
def news():
    items = News.query.order_by(News.id.desc()).all()
    # items.reverse()
    return render_template("admin/news.html", items=items)
@admin_bp.route("/news/add", methods=["GET", "POST"])
@admin_required
def add_news():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        news = News(title=title, description=description)
        db.session.add(news)
        db.session.commit()
        flash("News added successfully!", "success")
        return redirect(url_for("admin.news"))

    return render_template("admin/add_news.html")

@admin_bp.route("/news/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_news(id):
    news = News.query.get_or_404(id)
    if request.method == "POST":
        news.title = request.form.get("name")
        news.description = request.form.get("description")
        db.session.commit()
        flash("News updated successfully!", "successfull")
        return redirect(url_for("admin.news"))

    return render_template("admin/edit_news.html", item=news)

@admin_bp.route("/news/delete/<int:id>")
@admin_required
def delete_news(id):
    news = News.query.get_or_404(id)
    db.session.delete(news)
    db.session.commit()
    flash("News deleted successfully!", "success")
    return redirect(url_for("admin.news"))

@admin_bp.route("/news/swap/<int:id1>/<int:id2>")
@admin_required
def news_swap_between(id1, id2):
    item1 = News.query.get_or_404(id1)
    item2 = News.query.get_or_404(id2)

    item1.title, item2.title = item2.title, item1.title
    item1.description, item2.description = item2.description, item1.description
    item1.timestamp, item2.timestamp = item2.timestamp, item1.timestamp
    db.session.commit()
    flash("swapped successfully", "success")
    return redirect(url_for("admin.news_swap"))

@admin_bp.route("/news/swap")
@admin_required
def news_swap():
    items = News.query.order_by(News.id.desc()).all()
    return render_template("admin/news_swap.html", items=items)




# ------------------ GALLERY ------------------ #
@admin_bp.route("/gallery")
@admin_required
def gallery():
    items = Gallery.query.order_by(Gallery.id.desc()).all()
    return render_template("admin/gallery.html", items=items)

@admin_bp.route("/gallery/add", methods=["GET", "POST"])
@admin_required
def add_gallery():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        files = request.files.getlist("filename")

        filenames = []
        for file in files:
            if file:
                filenames.append(upload_to_imgbb(file))

        gallery = Gallery(title=title, description=description, images=",".join(filenames))
        db.session.add(gallery)
        db.session.commit()
        flash("Gallery item added successfully!", "success")
        return redirect(url_for("admin.gallery"))
    return render_template("admin/add_gallery.html")


@admin_bp.route("/gallery/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_gallery(id):
    # Get the specific gallery item from the database
    gallery = Gallery.query.get_or_404(id)
    if request.method == "POST":
        # 1. Update the title and description (this is the same as before)
        gallery.title = request.form.get("title")
        gallery.description = request.form.get("description")
        # 2. Get the list of newly uploaded files
        files = request.files.getlist("filename")
        if files and any(f.filename for f in files):
            new_filenames = []
            for file in files:
                if file:
                    image_url = upload_to_imgbb(file) 
                    new_filenames.append(image_url)
            gallery.images = ",".join(new_filenames)
            flash("Gallery item updated with new images successfully!", "success")
        else:
            images_to_keep = request.form.get("images_to_keep")
            gallery.images = images_to_keep if images_to_keep else ""
            flash("Gallery item text and images updated successfully!", "success")
        db.session.commit()
        return redirect(url_for("admin.gallery"))
    return render_template("admin/edit_gallery.html", item=gallery)
@admin_bp.route("/gallery/delete/<int:id>")
@admin_required
def delete_gallery(id):
    gallery = Gallery.query.get_or_404(id)
    db.session.delete(gallery)
    db.session.commit()
    flash("Gallery item deleted successfully!", "success")
    return redirect(url_for("admin.gallery"))

@admin_bp.route("/gallery/swap/<int:id1>/<int:id2>")
@admin_required
def gallery_swap_between(id1, id2):
    item1 = Gallery.query.get_or_404(id1)
    item2 = Gallery.query.get_or_404(id2)

    item1.title, item2.title = item2.title, item1.title
    item1.description, item2.description = item2.description, item1.description
    item1.images, item2.images = item2.images, item1.images
    item1.timestamp, item2.timestamp = item2.timestamp, item1.timestamp
    db.session.commit()
    flash("swapped successfully", "success")
    return redirect(url_for("admin.gallery_swap"))

@admin_bp.route("/gallery/swap")
@admin_required
def gallery_swap():
    items = Gallery.query.order_by(Gallery.id.desc()).all()
    return render_template("admin/gallery_swap.html", items=items)


