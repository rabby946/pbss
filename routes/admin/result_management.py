from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Result, db
from utils import admin_required
import cloudinary.uploader
from . import admin_bp

# ------------------ RESULTS ------------------ #

@admin_bp.route("/results", methods=["GET"])
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
            return redirect(url_for("admin_bp.add_result"))
        upload_result = cloudinary.uploader.upload(file,resource_type="raw")
        pdf_url = upload_result["secure_url"]
        result = Result(title=title, file_url=pdf_url)
        db.session.add(result)
        db.session.commit()
        flash("Result added successfully!", "success")
        return redirect(url_for("admin_bp.results"))
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
        return redirect(url_for("admin_bp.results"))
    return render_template("admin/edit_result.html", item=result)

@admin_bp.route("/results/delete/<int:id>")
@admin_required
def delete_result(id):
    result = Result.query.get_or_404(id)
    db.session.delete(result)
    db.session.commit()
    flash("Result deleted successfully!", "success")
    return redirect(url_for("admin_bp.results"))

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
    return redirect(url_for("admin_bp.result_swap"))

@admin_bp.route("/result/swap")
@admin_required
def result_swap():
    items = Result.query.order_by(Result.id.desc()).all()
    return render_template("admin/result_swap.html", items=items)