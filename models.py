# models.py
from datetime import datetime
from extensions import db

# -----------------------
# Existing models (kept as-is)
# -----------------------

# News
class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Gallery (multiple images)
class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    images = db.Column(db.JSON)  # list of image URLs
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Committees
class Committee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    designation = db.Column(db.String(200))
    image_url = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# MPOs
class MPO(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))  # can stay short
    designation = db.Column(db.Text)  # long descriptions
    image_url = db.Column(db.String(500))  # imgbb urls can be long
    timestamp = db.Column(db.DateTime)

# Results (file uploads / published results)
class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    file_url = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)



# Reports (contact / complaint)
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    purpose = db.Column(db.String(100))
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# -----------------------
# New/updated schema models
# -----------------------

# Users - central auth table
class User(db.Model):
    __tablename__ = 'users'
    email = db.Column(db.String(255), nullable=True)

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_type = db.Column(
        db.Enum('student', 'teacher', 'admin', name='user_types'),
        nullable=False,
        default='student'
    )
    password = db.Column(db.String(255), nullable=False)
    last_login = db.Column(db.DateTime)

    # One-to-one relationships to teacher/student (if present)
    teacher = db.relationship(
        'Teacher',
        back_populates='user',
        uselist=False,
        cascade='all, delete-orphan',
        passive_deletes=True
    )
    student = db.relationship(
        'Student',
        back_populates='user',
        uselist=False,
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    def __repr__(self):
        return f"<User id={self.id} type={self.user_type}>"


# School classes (avoid using python reserved 'class' -> use SchoolClass)
class SchoolClass(db.Model):
    __tablename__ = 'classes'

    id = db.Column(db.BigInteger, primary_key=True)
    teacher_id = db.Column(db.BigInteger, db.ForeignKey('teachers.id', ondelete='CASCADE'), nullable=True)
    name = db.Column(db.String(100), nullable=False)   
    section = db.Column(db.String(50))
    reference = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    new_column = db.Column(db.BigInteger)  # placeholder if needed

    # Relationships
    teacher = db.relationship('Teacher', back_populates='classes', passive_deletes=True)
    students = db.relationship('Student', back_populates='class_', cascade='all, delete-orphan', passive_deletes=True)
    assigned_subjects = db.relationship('AssignedSubject', back_populates='class_', cascade='all, delete-orphan', passive_deletes=True)
    subjects = db.relationship('Subject', backref='class_', passive_deletes=True)

    def __repr__(self):
        return f"<SchoolClass id={self.id} name={self.name} section={self.section}>"


# Subjects table
class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    class_id = db.Column(db.BigInteger, db.ForeignKey('classes.id', ondelete='SET NULL'), nullable=True)
    code = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    assigned = db.relationship('AssignedSubject', back_populates='subject', cascade='all, delete-orphan', passive_deletes=True)
    registered = db.relationship('RegisteredSubject', back_populates='subject', cascade='all, delete-orphan', passive_deletes=True)
    exam_results = db.relationship('ExamResult', back_populates='subject', cascade='all, delete-orphan', passive_deletes=True)
    routines = db.relationship('Routine', back_populates='subject', cascade='all, delete-orphan', passive_deletes=True)

    def __repr__(self):
        return f"<Subject id={self.id} name={self.name}>"


# Assigned subjects: which teacher teaches which subject in which class
class AssignedSubject(db.Model):
    __tablename__ = 'assigned_subjects'

    id = db.Column(db.BigInteger, primary_key=True)
    teacher_id = db.Column(db.BigInteger, db.ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.BigInteger, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    class_id = db.Column(db.BigInteger, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    teacher = db.relationship('Teacher', back_populates='assigned_subjects', passive_deletes=True)
    subject = db.relationship('Subject', back_populates='assigned', passive_deletes=True)
    class_ = db.relationship('SchoolClass', back_populates='assigned_subjects', passive_deletes=True)

    def __repr__(self):
        return f"<AssignedSubject id={self.id} teacher={self.teacher_id} subject={self.subject_id} class={self.class_id}>"


# Registered subjects: which student registered for which subject (used for marks reporting)
class RegisteredSubject(db.Model):
    __tablename__ = 'registered_subjects'

    id = db.Column(db.BigInteger, primary_key=True)
    subject_id = db.Column(db.BigInteger, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.BigInteger, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    subject = db.relationship('Subject', back_populates='registered', passive_deletes=True)
    student = db.relationship('Student', back_populates='registered_subjects', passive_deletes=True)

    def __repr__(self):
        return f"<RegisteredSubject id={self.id} student={self.student_id} subject={self.subject_id}>"


# Transactions (payments)
class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.BigInteger, primary_key=True)
    student_id = db.Column(db.BigInteger, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    payment_method = db.Column(db.String(100))
    amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    reference = db.Column(db.String(255))
    status = db.Column(db.Enum('pending', 'paid', 'failed', name='transaction_status'), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    student = db.relationship('Student', back_populates='transactions', passive_deletes=True)

    def __repr__(self):
        return f"<Transaction id={self.id} student={self.student_id} amount={self.amount} status={self.status}>"


# Attendances
class Attendance(db.Model):
    __tablename__ = 'attendances'

    id = db.Column(db.BigInteger, primary_key=True)
    student_id = db.Column(db.BigInteger, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.Enum('present', 'absent', 'late', name='attendance_status'), nullable=False, default='present')
    check_in_at = db.Column(db.Time)
    check_out_at = db.Column(db.Time)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    student = db.relationship('Student', back_populates='attendances', passive_deletes=True)

    def __repr__(self):
        return f"<Attendance id={self.id} student={self.student_id} date={self.created_at.date()} status={self.status}>"

class ExamResult(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.BigInteger, primary_key=True)
    student_id = db.Column(db.BigInteger, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.BigInteger, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    exam_type = db.Column(db.Enum('midterm', 'final', 'quiz', 'class_test', name='exam_types'), nullable=False)
    marks = db.Column(db.Float)
    grade = db.Column(db.String(10))   
    exam_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    student = db.relationship('Student', back_populates='exam_results', passive_deletes=True)
    subject = db.relationship('Subject', back_populates='exam_results', passive_deletes=True)

    def __repr__(self):
        return f"<ExamResult id={self.id} student={self.student_id} subject={self.subject_id} marks={self.marks}>"

class Routine(db.Model):
    __tablename__ = 'routines'

    id = db.Column(db.BigInteger, primary_key=True)
    teacher_id = db.Column(db.BigInteger, db.ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.BigInteger, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    day = db.Column(
        db.Enum('Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', name='week_days'),
        nullable=False
    )
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, nullable=True)  # optional, can be auto-calculated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    room = db.Column(db.Text)
    # relationships
    teacher = db.relationship('Teacher', back_populates='routines', passive_deletes=True)
    subject = db.relationship('Subject', back_populates='routines', passive_deletes=True)

    def __repr__(self):
        return f"<Routine {self.day} {self.start_time}-{self.end_time}>"


# Teachers (new)
class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    position = db.Column(db.String(200))
    designation = db.Column(db.String(200))
    qualification = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    address = db.Column(db.String(255))
    image_url = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    user = db.relationship('User', back_populates='teacher', passive_deletes=True)
    classes = db.relationship('SchoolClass', back_populates='teacher', cascade='all, delete-orphan', passive_deletes=True)
    assigned_subjects = db.relationship('AssignedSubject', back_populates='teacher', cascade='all, delete-orphan', passive_deletes=True)
    routines = db.relationship('Routine', back_populates='teacher', cascade='all, delete-orphan', passive_deletes=True)

    def __repr__(self):
        return f"<Teacher id={self.id} name={self.name}>"


# Students (new)
class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    studentID = db.Column(db.String(100), unique=True)   # your 'studentID' field
    class_id = db.Column(db.BigInteger, db.ForeignKey('classes.id', ondelete='SET NULL'), nullable=True)
    roll = db.Column(db.String(50))
    address = db.Column(db.String(255))
    blood_group = db.Column(db.String(20))
    batch = db.Column(db.BigInteger)
    due_amount = db.Column(db.Numeric(10, 2), default=0.00)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    user = db.relationship('User', back_populates='student', passive_deletes=True)
    class_ = db.relationship('SchoolClass', back_populates='students', passive_deletes=True)
    transactions = db.relationship('Transaction', back_populates='student', cascade='all, delete-orphan', passive_deletes=True)
    attendances = db.relationship('Attendance', back_populates='student', cascade='all, delete-orphan', passive_deletes=True)
    registered_subjects = db.relationship('RegisteredSubject', back_populates='student', cascade='all, delete-orphan', passive_deletes=True)
    exam_results = db.relationship('ExamResult', back_populates='student', cascade='all, delete-orphan', passive_deletes=True)

    def __repr__(self):
        return f"<Student id={self.id} name={self.name} studentID={self.studentID}>"
