from flask import (
    render_template, request, redirect, url_for, flash
)
from . import admin_bp
from models import Student, User, db, SchoolClass, Teacher, Subject, RegisteredSubject
from utils import admin_required
from werkzeug.security import generate_password_hash

@admin_bp.route("/students", methods=["GET", "POST"])
@admin_required
def list_students():
    # default to first class if none provided
    class_id = request.args.get("class_id", type=int) or 0
    if request.method == "POST":
        action = request.form.get("action")
        student_id = request.form.get("student_id", type=int)
        
        if not action or not student_id:
            flash("Invalid request.", "danger")
            return redirect(url_for("admin_bp.list_students"))

        student = Student.query.get(student_id)
        if not student:
            flash("Student not found.", "warning")
            return redirect(url_for("admin_bp.list_students"))

        if action == "delete":
            db.session.delete(student)
            db.session.commit()
            flash("Student deleted successfully.", "success")
            return redirect(url_for("admin_bp.list_students"))

        flash("Unknown action.", "warning")
        return redirect(url_for("admin_bp.list_students"))
    if class_id:
        students = Student.query.filter_by(class_id=class_id).order_by(Student.roll.asc()).all()
    else:
        students = Student.query.order_by(Student.class_id.asc(), Student.roll.asc()).limit(200).all()
    classes = SchoolClass.query.order_by(SchoolClass.id.asc()).all()
    return render_template("admin/students.html",students=students,classes=classes,selected_class_id=class_id,)

@admin_bp.route("/students/add", methods=["GET", "POST"])
@admin_required
def add_student():
    classes = SchoolClass.query.order_by(SchoolClass.name.asc()).all()

    if request.method == "POST":
        # fetch and validate form fields
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        class_id = request.form.get("class_id", type=int)
        address = request.form.get("address", "").strip()
        batch = 22
        roll = request.form.get("roll", "").strip()

        if not (name and email and studentID and class_id):
            flash("Name, email, batch, and roll are required.", "danger")
            return render_template("admin/add_student.html", classes=classes)
        
        student_class = SchoolClass.query.get(class_id)
        class_name = student_class.name.upper()
        if class_name == "SIX":
            batch = 2030
        elif class_name == "SEVEN":
            batch = 2029
        elif class_name == "EIGHT":
            batch = 2028
        elif class_name == "NINE":
            batch = 2027
        elif class_name == "TEN":
            batch = 2026
            
        if batch and roll:
            studentID = f"{batch}-{roll}"
        else:
            studentID = None
        if Student.query.filter_by(studentID=studentID).first():
            flash(f'For student ID {studentID}, A student with this ID already exists. Maybe someone in this batch had the same roll number. Try with different roll number', "warning")
            return render_template("admin/add_student.html", classes=classes)
        
        hashed = generate_password_hash(studentID)
        user = User(email=email, password=hashed, user_type="student")
        db.session.add(user)
        db.session.flush() 
        student = Student(name=name,user_id=user.id,class_id=class_id,studentID=studentID,address=address,batch=batch,roll=roll,)
        db.session.add(student)
        db.session.flush() 
        subjects = Subject.query.filter_by(class_id=class_id).all()
        for item in subjects:
            obj = RegisteredSubject(subject_id=item.id, student_id=student.id, status="active",)
            db.session.add(obj)
        db.session.commit()

        flash(f"Student added successfully! (Student ID: {studentID})", "success")
        return redirect(url_for("admin_bp.list_students"))

    return render_template("admin/add_student.html", classes=classes)


@admin_bp.route("/students/edit/<int:student_id>", methods=["GET", "POST"])
@admin_required
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    classes = SchoolClass.query.order_by(SchoolClass.name.asc()).all()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        class_id = request.form.get("class_id", type=int)
        address = request.form.get("address", "").strip()
        batch = request.form.get("batch", type=int)
        roll = request.form.get("roll", "").strip()
        if batch and roll:
            studentID = f"{batch}-{roll}"
        else:
            studentID = student.studentID 

        if not (name and email and studentID):
            flash("Name, email and studentID are required.", "danger")
            return render_template("admin/edit_student.html", student=student, classes=classes)

        # update linked user
        user = User.query.get_or_404(student.user_id)

        # ✅ check if email changed
        if user.email != email:
            if User.query.filter(User.email == email, User.id != user.id).first():
                flash("Email already in use by another account.", "warning")
                return render_template("admin/edit_student.html", student=student, classes=classes)
            user.email = email
        if student.studentID != studentID:
            if Student.query.filter(Student.studentID == studentID, Student.id != student.id).first():
                flash("Student ID already used by another student.", "warning")
                return render_template("admin/edit_student.html", student=student, classes=classes)
            student.studentID = studentID

        student.name = name
        student.class_id = class_id
        student.address = address
        student.batch = batch
        student.roll = roll

        db.session.commit()
        flash("Student updated successfully.", "success")
        return redirect(url_for("admin_bp.list_students"))

    return render_template("admin/edit_student.html", student=student, classes=classes)
