from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from datetime import datetime, time, date
from werkzeug.security import check_password_hash
from models import db, Student, User, ExamResult, Attendance, RegisteredSubject, Subject, Transaction, Routine, News, Teacher
from extensions import db
from utils import student_required, upload_image
from calendar import monthrange
from decimal import Decimal 
student_bp = Blueprint('student_bp', __name__, url_prefix='/student')
import time, json, requests
from config import Config
import time
import requests
from decimal import Decimal
from flask import request, session, redirect, url_for, flash, jsonify, current_app
from config import Config

@student_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        studentID = request.form.get('nid')
        password = request.form.get('password')
        student = Student.query.filter_by(studentID=studentID).first()
        if not student:
            flash("Student not found.", "danger")
            return redirect(url_for('public.login'))
        user = User.query.get(student.user_id)
        if user and user.password == password:
            session['student_id'] = student.id
            session['student_name'] = student.name
            flash("Login successful!", "success")
            return redirect(url_for('student_bp.dashboard'))
        flash("Invalid credentials.", "danger")
    return render_template('public/login.html')


@student_bp.route('/logout')
@student_required
def student_logout():
    session.pop('student_id', None)
    session.pop('student_name', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('public.login'))

@student_bp.route('/change-password', methods=["GET", "POST"])
@student_required
def changePassword():
    if request.method == "POST":
        old_pass = request.form.get('old-pass', '').strip()
        new_pass = request.form.get('new-pass', '').strip()
        student = Student.query.get_or_404(session['student_id'])
        user = student.user
        if user and user.password == old_pass:
            user.password = new_pass
            db.session.commit()
            flash(f'password updated successfully', 'success')
        else:
            flash(f'wrong password', 'error')
        return redirect(request.url)
    return render_template("student/changepassword.html")
        

@student_bp.route('/dashboard')
@student_required
def dashboard():
    student = Student.query.get(session['student_id'])
    recent_news = News.query.order_by(News.timestamp.desc()).limit(5).all()
    results_count = ExamResult.query.filter_by(student_id=student.id).count()
    attendance_count = Attendance.query.filter_by(student_id=student.id).count()
    return render_template('student/dashboard.html',student=student,notices=recent_news,results_count=results_count,attendance_count=attendance_count)


@student_bp.route('/profile', methods=['GET', 'POST'])
@student_required
def profile():
    student = Student.query.get_or_404(session['student_id'])
    user = student.user  
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        address = request.form.get('address', '').strip()
        blood_group = request.form.get('blood_group', '').strip()
        image_file = request.files.get('image')
        student.name = name
        student.address = address
        student.blood_group = blood_group
        if image_file and image_file.filename:
            student.image_url = upload_image(image_file)
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for('student_bp.profile'))
    return render_template('student/profile.html', student=student, user=user)

from sqlalchemy.orm import aliased
@student_bp.route('/routines', methods=['GET'])
@student_required
def routines():
    student = Student.query.get_or_404(session['student_id'])
    selected_day = request.args.get('day', 'Monday')
    if not student.class_id:
        flash("You are not assigned to any class yet.", "warning")
        return render_template('student/routines.html',routines=[],selected_day=selected_day,student=student)
    reg_sub = aliased(RegisteredSubject)
    routines = (Routine.query.join(Subject, Routine.subject_id == Subject.id).join(Teacher, Routine.teacher_id == Teacher.id).join(reg_sub, reg_sub.subject_id == Subject.id).filter(Routine.day == selected_day).filter(reg_sub.student_id == student.id).filter(reg_sub.status == 'active').order_by(Routine.start_time.asc()).add_entity(Subject).add_entity(Teacher).all())
    return render_template('student/routines.html',routines=routines,selected_day=selected_day,student=student)

@student_bp.route('/notices')
@student_required
def notices():
    news = News.query.order_by(News.timestamp.desc()).all()
    return render_template('student/notices.html', news=news)

@student_bp.route('/attendance', methods=['GET'])
@student_required
def attendance():
    student_id = session["student_id"]
    date_str = request.args.get('date')
    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    except ValueError:
        flash("Invalid date format.", "danger")
        return redirect(url_for('admin_bp.attendance', student_id=student_id))
    if selected_date > date.today():
        flash("You can't view attendance for future dates.", "warning")
        return redirect(url_for('admin_bp.attendance', student_id=student_id))
    student = Student.query.get_or_404(student_id)
    attendance_record = (Attendance.query.filter_by(student_id=student_id).filter(db.func.date(Attendance.created_at) == selected_date).first())
    attendance_dict = {student.id: attendance_record.status} if attendance_record else {}
    return render_template('student/attendance.html',student=student,attendance_dict=attendance_dict,selected_date=selected_date,today=date.today(), 
        all_attendance_records=[{
        'date': a.created_at.strftime('%Y-%m-%d'),
        'status': a.status
        } for a in Attendance.query.filter_by(student_id=student.id).all()]
    )
@student_bp.route('/results', methods=['GET'])
@student_required
def results():
    student = Student.query.get_or_404(session['student_id'])
    selected_subject_id = request.args.get('subject', 'all')
    selected_exam_type = request.args.get('exam_type', 'all')
    active_subjects = (Subject.query.join(RegisteredSubject, RegisteredSubject.subject_id == Subject.id).filter(RegisteredSubject.student_id == student.id, RegisteredSubject.status == 'active').order_by(Subject.name.asc()).all())
    results = []
    if selected_subject_id != 'all' or selected_exam_type != 'all':
        subj_alias = aliased(Subject)
        query = ExamResult.query.filter(ExamResult.student_id == student.id)
        if selected_subject_id != 'all':
            query = query.filter(ExamResult.subject_id == int(selected_subject_id))
        else:
            query = query.filter(ExamResult.subject_id.in_([s.id for s in active_subjects]))
        if selected_exam_type != 'all':
            query = query.filter(ExamResult.exam_type == selected_exam_type)
        results = (query
            .join(subj_alias, ExamResult.subject_id == subj_alias.id)
            .add_columns(subj_alias.name.label('subject_name'),ExamResult.exam_type,ExamResult.marks,ExamResult.grade,ExamResult.exam_date)
            .order_by(ExamResult.exam_date.desc(), ExamResult.created_at.desc()).all()
        )
    exam_types = ['midterm', 'final', 'quiz', 'class_test']
    return render_template('student/results.html',student=student,active_subjects=active_subjects,exam_types=exam_types,results=results,selected_subject_id=selected_subject_id,selected_exam_type=selected_exam_type)

@student_bp.route('/payments', methods=['GET'])
@student_required
def payments():
    student_id = session['student_id']
    student = Student.query.get_or_404(student_id)
    transactions = Transaction.query.filter_by(student_id=student_id).order_by(Transaction.created_at.desc()).all()
    return render_template('student/payments.html', student=student, transactions=transactions)

# --- simple token cache ---
_bkash_token_cache = {"token": None, "expires_at": 0}
def get_bkash_token(force_refresh: bool = False):
    # use cached token if still valid
    if not force_refresh and _bkash_token_cache["token"] and _bkash_token_cache["expires_at"] > time.time():
        print(_bkash_token_cache["token"])
        return _bkash_token_cache["token"]

    token_url = f"{Config.BKASH_BASE_URL}/tokenized/checkout/token/grant"
    headers = {
        "Content-Type": "application/json",
        "username": Config.BKASH_USERNAME,
        "password": Config.BKASH_PASSWORD
    }
    payload = {
        "app_key": Config.BKASH_APP_KEY,
        "app_secret": Config.BKASH_APP_SECRET
    }

    try:
        resp = requests.post(token_url, headers=headers, json=payload, timeout=15)
        token_json = resp.json()
        current_app.logger.info(f"bKash token response: {token_json}")
    except Exception as e:
        current_app.logger.error(f"bKash token request failed: {e}")
        return None

    id_token = token_json.get("id_token") or token_json.get("idToken")
    expires_in = token_json.get("expires_in", 3600)

    if not id_token:
        current_app.logger.error(f"Failed to obtain bKash token: {token_json}")
        return None

    _bkash_token_cache["token"] = id_token
    _bkash_token_cache["expires_at"] = time.time() + int(expires_in) - 10
    return id_token


# --- initiate payment ---
@student_bp.route('/initiate-bkash-payment', methods=['POST'])
@student_required
def initiate_bkash_payment():
    student = Student.query.get_or_404(session['student_id'])

    try:
        amount = Decimal(request.form.get('amount', '0').strip())
    except Exception:
        flash("Invalid amount entered.", "danger")
        return redirect(url_for('student_bp.payments'))

    if amount <= 0:
        flash("Amount must be positive.", "warning")
        return redirect(url_for('student_bp.payments'))

    id_token = get_bkash_token()
    if not id_token:
        flash("bKash authentication failed. Try again later.", "danger")
        return redirect(url_for('student_bp.payments'))

    create_url = f"{Config.BKASH_BASE_URL}{Config.BKASH_CREATE_PAYMENT_URL}"
    headers = {
        "Content-Type": "application/json",
        "authorization": id_token,
        "x-app-key": Config.BKASH_APP_KEY
    }

    merchant_invoice = f"INV-{student.id}-{int(time.time())}"
    callback_url = url_for('student_bp.bkash_execute_callback', _external=True)
    payload = {
        "mode": "0011",
        "payerReference": str(student.id),
        "callbackURL": callback_url,
        "amount": str(amount),
        "currency": "BDT",
        "intent": "sale",
        "merchantInvoiceNumber": merchant_invoice
    }

    try:
        resp = requests.post(create_url, headers=headers, json=payload, timeout=10)
        result = resp.json()
    except Exception as e:
        current_app.logger.error("bKash create payment failed: %s", e)
        flash("Failed to connect to bKash. Try again.", "danger")
        return redirect(url_for('student_bp.payments'))

    bkash_url = result.get("bkashURL") or result.get("checkoutURL")
    payment_id = result.get("paymentID") or result.get("paymentId")

    if not bkash_url:
        msg = result.get("message") or "Unknown bKash error"
        flash(f"bKash Error: {msg}", "danger")
        return redirect(url_for('student_bp.payments'))

    # save pending transaction
    txn = Transaction(
        student_id=student.id,
        amount=amount,
        payment_method="bKash",
        status="pending",
        payment_id=payment_id,
        merchant_invoice_number=merchant_invoice
    )
    db.session.add(txn)
    db.session.commit()

    return redirect(bkash_url)

# --- callback after student completes payment ---
@student_bp.route('/bkash/execute-callback', methods=['GET'])
def bkash_execute_callback():
    payment_id = request.args.get('paymentID') or request.args.get('paymentId')
    if not payment_id:
        flash("Invalid payment response from bKash.", "danger")
        return redirect(url_for('student_bp.payments'))

    id_token = get_bkash_token()
    if not id_token:
        flash("bKash authentication failed.", "danger")
        return redirect(url_for('student_bp.payments'))

    execute_url = f"{Config.BKASH_BASE_URL}{Config.BKASH_EXECUTE_PAYMENT_URL}"
    headers = {
        "Content-Type": "application/json",
        "authorization": id_token,
        "x-app-key": Config.BKASH_APP_KEY
    }
    payload = {"paymentID": payment_id}

    try:
        resp = requests.post(execute_url, headers=headers, json=payload, timeout=10)
        result = resp.json()
    except Exception as e:
        current_app.logger.error("bKash execute payment failed: %s", e)
        flash("Payment verification failed. Contact admin.", "danger")
        return redirect(url_for('student_bp.payments'))

    status = result.get("transactionStatus") or result.get("status") or "failed"
    amount = result.get("amount") or result.get("paidAmount")
    merchant_invoice = result.get("merchantInvoiceNumber")
    trx_id = result.get("trxID")
    
    try:
        amount_decimal = Decimal(str(amount)) if amount else Decimal("0")
    except Exception:
        amount_decimal = Decimal("0")

    # find transaction
    txn = Transaction.query.filter(
        (Transaction.payment_id == payment_id) |
        (Transaction.merchant_invoice_number == merchant_invoice)
    ).first()

    if not txn:
        txn = Transaction(
            student_id=session.get('student_id'),
            amount=amount_decimal,
            payment_method="bKash",
            status=status,
            payment_id=payment_id,
            trx_id = trx_id,
            merchant_invoice_number=merchant_invoice
        )
        db.session.add(txn)

    else:
        txn.status = "paid" if status.lower() == "completed" else "failed"
        txn.trx_id = trx_id
        txn.amount = amount_decimal

    # update student due
    if txn.status == "paid":
        student = Student.query.get(txn.student_id)
        if student:
            student.due_amount -= amount_decimal
            if student.due_amount < 0:
                flash(f"You have overpaid by {abs(student.due_amount)} BDT. This overpaid amount will be adjust with your further transactions. Thank you!", "info")
    db.session.commit()
    flash("Payment processed successfully." if txn.status == "paid" else "Payment failed.", "success" if txn.status=="paid" else "warning")
    return redirect(url_for('student_bp.payments'))
