from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Subject, SchoolClass, Gallery
from datetime import datetime
from . import admin_bp
from utils import admin_required, upload_image

@admin_bp.route('/subjects', methods=['GET', 'POST'])
@admin_required
def manage_subjects():
    classes = SchoolClass.query.order_by(SchoolClass.name).all()
    subjects = Subject.query.order_by(Subject.class_id.desc()).all()

    if request.method == 'POST' and request.form.get('action') == 'add':
        try:
            name = request.form['name']
            code = request.form.get('code')
            class_id = request.form.get('class_id') or None
            # Check if subject code already exists
            if Subject.query.filter_by(code=code).first():
                flash("This Subject Code already exists", "info")
                return redirect(url_for("admin_bp.manage_subjects"))

            # Check if subject name already exists in the same class
            if Subject.query.filter_by(class_id=class_id, name=name).first():
                flash("This Subject already exists in this class", "info")
                return redirect(url_for("admin_bp.manage_subjects"))

            new_subject = Subject(
                name=name,
                code=code,
                class_id=class_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(new_subject)
            db.session.commit()
            flash(f"Subject '{name}' added successfully!", 'success')
            return redirect(url_for('admin_bp.manage_subjects'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding subject: {str(e)}", 'danger')

    if request.method == 'POST' and request.form.get('action') == 'edit':
        try:
            subject_id = request.form['subject_id']
            subject = Subject.query.get_or_404(subject_id)

            subject.name = request.form['name']
            subject.code = request.form.get('code')
            subject.class_id = request.form.get('class_id') or None
            subject.updated_at = datetime.utcnow()

            db.session.commit()
            flash(f"Subject '{subject.name}' updated successfully!", 'success')
            return redirect(url_for('admin_bp.manage_subjects'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating subject: {str(e)}", 'danger')

    delete_id = request.args.get('delete_id')
    if delete_id:
        try:
            subject = Subject.query.get_or_404(delete_id)
            db.session.delete(subject)
            db.session.commit()
            flash(f"Subject '{subject.name}' deleted successfully!", 'info')
            return redirect(url_for('admin_bp.manage_subjects'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error deleting subject: {str(e)}", 'danger')

    return render_template('admin/subjects.html', subjects=subjects, classes=classes)


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
                filenames.append(upload_image(file))

        gallery = Gallery(title=title, description=description, images=",".join(filenames))
        db.session.add(gallery)
        db.session.commit()
        flash("Gallery item added successfully!", "success")
        return redirect(url_for("admin_bp.gallery"))
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
                    image_url = upload_image(file) 
                    new_filenames.append(image_url)
            gallery.images = ",".join(new_filenames)
            flash("Gallery item updated with new images successfully!", "success")
        else:
            images_to_keep = request.form.get("images_to_keep")
            gallery.images = images_to_keep if images_to_keep else ""
            flash("Gallery item text and images updated successfully!", "success")
        db.session.commit()
        return redirect(url_for("admin_bp.gallery"))
    return render_template("admin/edit_gallery.html", item=gallery)
@admin_bp.route("/gallery/delete/<int:id>")
@admin_required
def delete_gallery(id):
    gallery = Gallery.query.get_or_404(id)
    db.session.delete(gallery)
    db.session.commit()
    flash("Gallery item deleted successfully!", "success")
    return redirect(url_for("admin_bp.gallery"))

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
    return redirect(url_for("admin_bp.gallery_swap"))

@admin_bp.route("/gallery/swap")
@admin_required
def gallery_swap():
    items = Gallery.query.order_by(Gallery.id.desc()).all()
    return render_template("admin/gallery_swap.html", items=items)

