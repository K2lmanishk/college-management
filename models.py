from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()
ACADEMIC_YEAR = "2025-2026"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512))
    role = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(100))
    profile_pic = db.Column(db.String(200), default='default.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    student_profile = db.relationship('Student', backref='user', uselist=False)
    faculty_profile = db.relationship('Faculty', backref='user', uselist=False)
    sent_notifications = db.relationship('Notification', foreign_keys='Notification.created_by', backref='creator', lazy=True)
    personal_notifications = db.relationship('Notification', foreign_keys='Notification.specific_user_id', backref='specific_user', lazy=True)

class Program(db.Model):
    __tablename__ = 'programs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True)
    duration_years = db.Column(db.Integer)
    description = db.Column(db.Text)
    
    subjects = db.relationship('Subject', backref='program', lazy=True)
    students = db.relationship('Student', backref='program', lazy=True)
    timetable_entries = db.relationship('Timetable', backref='program', lazy=True)
    fee_structures = db.relationship('ProgramSemesterFee', backref='program', lazy=True)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    roll_no = db.Column(db.String(20), unique=True, nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'))
    semester = db.Column(db.String(50))  # e.g., 'Semester 1'
    dob = db.Column(db.Date)
    phone = db.Column(db.String(15))
    address = db.Column(db.Text)
    parent_contact = db.Column(db.String(15))
    
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)
    marks = db.relationship('Marks', backref='student', lazy=True)
    fee_records = db.relationship('Fee', backref='student', lazy=True)

class Faculty(db.Model):
    __tablename__ = 'faculty'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    department = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    qualification = db.Column(db.String(200))
    joining_date = db.Column(db.Date)
    
    assignments = db.relationship('FacultyAssignment', backref='faculty', lazy=True)
    timetable_entries = db.relationship('Timetable', backref='faculty', lazy=True)

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=True)
    semester = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True)
    credits = db.Column(db.Integer)
    type = db.Column(db.String(20))  # Theory, Practical, etc.
    
    assignments = db.relationship('FacultyAssignment', backref='subject', lazy=True)
    attendance = db.relationship('Attendance', backref='subject', lazy=True)
    marks = db.relationship('Marks', backref='subject', lazy=True)
    timetable_entries = db.relationship('Timetable', backref='subject', lazy=True)

class FacultyAssignment(db.Model):
    __tablename__ = 'faculty_assignments'
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    academic_year = db.Column(db.String(20))

class Timetable(db.Model):
    __tablename__ = 'timetable'
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(20))
    time_slot = db.Column(db.String(50))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'))
    room_no = db.Column(db.String(20))
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=True)
    semester = db.Column(db.String(50))

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    date = db.Column(db.Date, default=datetime.utcnow)
    status = db.Column(db.String(10))

class Marks(db.Model):
    __tablename__ = 'marks'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    exam_type = db.Column(db.String(50))
    max_marks = db.Column(db.Integer)
    obtained_marks = db.Column(db.Float)

class Fee(db.Model):
    __tablename__ = 'fees'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    amount = db.Column(db.Float)
    due_date = db.Column(db.Date)
    paid_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='Pending')
    transaction_id = db.Column(db.String(100))
    payment_date = db.Column(db.DateTime)
    payment_method = db.Column(db.String(50))
    remarks = db.Column(db.Text)

class Notice(db.Model):
    __tablename__ = 'notices'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    audience = db.Column(db.String(20))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default='general')
    audience = db.Column(db.String(20), nullable=False)
    specific_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    expiry_date = db.Column(db.Date, nullable=True)

class ProgramSemesterFee(db.Model):
    __tablename__ = 'program_semester_fees'
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    semester = db.Column(db.String(50), nullable=False)
    fee_amount = db.Column(db.Float, nullable=False)
    academic_year = db.Column(db.String(20), default=ACADEMIC_YEAR)  # Added column
    
    # REMOVE this line – the backref is already defined in Program
    # program = db.relationship('Program', backref='fee_structures')
    # Add these classes at the VERY END of models.py (not inside any other class)

class Exam(db.Model):
    __tablename__ = 'exams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    semester = db.Column(db.String(50), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)
    max_marks = db.Column(db.Integer, default=100)
    passing_marks = db.Column(db.Integer, default=40)
    academic_year = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    program = db.relationship('Program', backref='exams')
    subject = db.relationship('Subject', backref='exams')
    results = db.relationship('ExamResult', backref='exam', cascade='all, delete-orphan')


class ExamResult(db.Model):
    __tablename__ = 'exam_results'
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    obtained_marks = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(5))
    remarks = db.Column(db.String(200))
    entered_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    entered_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student', backref='exam_results')
    entered_by_user = db.relationship('User', backref='entered_results')

# ========== HOSTEL MANAGEMENT ==========
class Hostel(db.Model):
    __tablename__ = 'hostels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    total_rooms = db.Column(db.Integer)
    warden_name = db.Column(db.String(100))
    warden_phone = db.Column(db.String(15))

class HostelRoom(db.Model):
    __tablename__ = 'hostel_rooms'
    id = db.Column(db.Integer, primary_key=True)
    hostel_id = db.Column(db.Integer, db.ForeignKey('hostels.id'))
    room_number = db.Column(db.String(20), nullable=False)
    capacity = db.Column(db.Integer, default=2)
    occupied = db.Column(db.Integer, default=0)
    rent_per_month = db.Column(db.Float)
    hostel = db.relationship('Hostel', backref='rooms')

class HostelAllocation(db.Model):
    __tablename__ = 'hostel_allocations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('hostel_rooms.id'))
    allocated_date = db.Column(db.Date, default=datetime.utcnow)
    vacated_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='Active')  # Active, Vacated
    student = db.relationship('Student', backref='hostel_allocation')
    room = db.relationship('HostelRoom', backref='allocations')

# ========== TRANSPORT MANAGEMENT ==========
class TransportRoute(db.Model):
    __tablename__ = 'transport_routes'
    id = db.Column(db.Integer, primary_key=True)
    route_name = db.Column(db.String(100), nullable=False)
    vehicle_number = db.Column(db.String(20))
    driver_name = db.Column(db.String(100))
    driver_phone = db.Column(db.String(15))
    fee_per_month = db.Column(db.Float)

class TransportStop(db.Model):
    __tablename__ = 'transport_stops'
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('transport_routes.id'))
    stop_name = db.Column(db.String(100))
    stop_order = db.Column(db.Integer)
    route = db.relationship('TransportRoute', backref='stops')

class TransportAllocation(db.Model):
    __tablename__ = 'transport_allocations'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    route_id = db.Column(db.Integer, db.ForeignKey('transport_routes.id'))
    stop_id = db.Column(db.Integer, db.ForeignKey('transport_stops.id'))
    allocated_date = db.Column(db.Date, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Active')
    student = db.relationship('Student', backref='transport')
    route = db.relationship('TransportRoute')
    stop = db.relationship('TransportStop')

# ========== LIBRARY MANAGEMENT ==========
class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100))
    isbn = db.Column(db.String(20), unique=True)
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    location = db.Column(db.String(50))

class BookIssue(db.Model):
    __tablename__ = 'book_issues'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    issue_date = db.Column(db.Date, default=datetime.utcnow)
    due_date = db.Column(db.Date)
    return_date = db.Column(db.Date, nullable=True)
    fine = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='Issued')  # Issued, Returned
    book = db.relationship('Book')
    student = db.relationship('Student')

# ========== PLACEMENT CELL ==========
class JobPost(db.Model):
    __tablename__ = 'job_posts'
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    eligibility = db.Column(db.String(200))
    last_date = db.Column(db.Date)
    posted_date = db.Column(db.Date, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Open')  # Open, Closed

class JobApplication(db.Model):
    __tablename__ = 'job_applications'
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job_posts.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    applied_date = db.Column(db.Date, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Applied')  # Applied, Shortlisted, Rejected
    job = db.relationship('JobPost')
    student = db.relationship('Student')

# ========== LEAVE APPLICATION ==========
class LeaveApplication(db.Model):
    __tablename__ = 'leave_applications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', foreign_keys=[user_id])
    approver = db.relationship('User', foreign_keys=[approved_by])

# ========== EVENT / HOLIDAY ==========
class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.Date)
    event_type = db.Column(db.String(20))  # Holiday, Event, Exam
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

# ========== COMPLAINT ==========
class Complaint(db.Model):
    __tablename__ = 'complaints'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')
    reply = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    student = db.relationship('Student', backref='complaints')

# ========== STUDY MATERIAL ==========
class StudyMaterial(db.Model):
    __tablename__ = 'study_materials'
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'))
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'))
    semester = db.Column(db.String(50))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    faculty = db.relationship('Faculty')
    program = db.relationship('Program')