# ============================================
# COLLEGE MANAGEMENT SYSTEM - RISE COLLEGE
# All Features Working + Mobile Responsive
# ============================================

from flask import make_response
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session, send_file, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Student, Faculty, Program, Subject, Attendance, Marks, Fee, Notice, FacultyAssignment, Timetable, Notification, ProgramSemesterFee
from sqlalchemy import text
from datetime import datetime, timedelta
import json
import os
import qrcode
import io
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Cloudinary Configuration
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'c63fe9c3a2f56ac7c926e52ac81330559a9ed36b38ee4c4b0180bc66a83279fa')
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///college.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')

# College Configuration
COLLEGE_NAME = "College Management System"
COLLEGE_ADDRESS = "Greater Noida, UP 201301"
COLLEGE_CONTACT = "+91-7004514869"
COLLEGE_EMAIL = "info@risecollege.edu.in"
ACADEMIC_YEAR = "2025-2026"

app = Flask(__name__)
app.config.from_object(Config)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def calculate_grade(percentage):
    if percentage >= 90:
        return 'A+'
    elif percentage >= 80:
        return 'A'
    elif percentage >= 70:
        return 'B+'
    elif percentage >= 60:
        return 'B'
    elif percentage >= 50:
        return 'C'
    elif percentage >= 40:
        return 'D'
    else:
        return 'F'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_sms(to_phone, message):
    try:
        from twilio.rest import Client
        account_sid = app.config.get('TWILIO_ACCOUNT_SID')
        auth_token = app.config.get('TWILIO_AUTH_TOKEN')
        from_number = app.config.get('TWILIO_PHONE_NUMBER')
        if not account_sid or not auth_token or not from_number:
            return False, "Twilio credentials not configured"
        client = Client(account_sid, auth_token)
        msg = client.messages.create(body=message, from_=from_number, to=to_phone)
        return True, msg.sid
    except Exception as e:
        return False, str(e)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_college_info():
    return {
        'now': datetime.utcnow(),
        'today': datetime.utcnow().date(),
        'college_name': COLLEGE_NAME,
        'college_address': COLLEGE_ADDRESS,
        'college_contact': COLLEGE_CONTACT,
        'college_email': COLLEGE_EMAIL,
        'academic_year': ACADEMIC_YEAR
    }

@app.route('/api/fee-summary')
@login_required
def fee_summary():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    total_fees = db.session.query(db.func.sum(Fee.amount)).scalar() or 0
    total_collected = db.session.query(db.func.sum(Fee.paid_amount)).scalar() or 0
    return jsonify({'total_fees': float(total_fees), 'total_collected': float(total_collected)})

@app.route('/api/program-enrollment')
@login_required
def program_enrollment():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    from models import Program, Student
    programs = Program.query.all()
    series = []
    labels = []
    for prog in programs:
        count = Student.query.filter_by(program_id=prog.id).count()
        if count > 0:
            series.append(count)
            labels.append(prog.name)
    if not series:
        series, labels = [45, 32, 28], ['BCA', 'BBA', 'BSc CS']  # fallback
    return jsonify({'series': series, 'labels': labels})
@app.context_processor
def utility_functions():
    import urllib.parse
    def whatsapp_link(phone, message):
        if not phone:
            return "#"
        # Clean phone number: remove spaces, ensure +91 if Indian 10-digit
        phone = ''.join(filter(str.isdigit, phone))
        if len(phone) == 10:
            phone = '91' + phone
        elif phone.startswith('0'):
            phone = '91' + phone[1:]
        encoded_msg = urllib.parse.quote(message)
        return f"https://wa.me/{phone}?text={encoded_msg}"
    return dict(whatsapp_link=whatsapp_link)

# ------------------------------
# AUTHENTICATION
# ------------------------------

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            session['user_role'] = user.role
            # Set flag to show download popup after redirect
            session['show_download_modal'] = True
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'faculty':
                return redirect(url_for('faculty_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

# ------------------------------
# ADMIN DASHBOARD
# ------------------------------
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    total_students = Student.query.count()
    total_faculty = Faculty.query.count()
    total_programs = Program.query.count()
    recent_notices = Notice.query.order_by(Notice.created_at.desc()).limit(5).all()
    return render_template('admin_dashboard.html',
                           total_students=total_students,
                           total_faculty=total_faculty,
                           total_programs=total_programs,
                           notices=recent_notices)


# ========== EXAM MANAGEMENT (ADMIN) ==========
@app.route('/admin/exams')
@login_required
def manage_exams():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    exams = Exam.query.order_by(Exam.exam_date.desc()).all()
    programs = Program.query.all()
    subjects = Subject.query.all()
    semesters = ['Semester 1','Semester 2','Semester 3','Semester 4','Semester 5','Semester 6','Semester 7','Semester 8']
    return render_template('admin_exams.html', exams=exams, programs=programs, subjects=subjects, semesters=semesters)

@app.route('/admin/exam/add', methods=['POST'])
@login_required
def add_exam():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    exam = Exam(
        name=request.form['name'],
        program_id=request.form['program_id'],
        semester=request.form['semester'],
        subject_id=request.form['subject_id'],
        exam_date=datetime.strptime(request.form['exam_date'], '%Y-%m-%d'),
        max_marks=int(request.form['max_marks']),
        passing_marks=int(request.form.get('passing_marks', 40)),
        academic_year=request.form.get('academic_year', ACADEMIC_YEAR)
    )
    db.session.add(exam)
    db.session.commit()
    flash('Exam added successfully', 'success')
    return redirect(url_for('manage_exams'))

@app.route('/admin/exam/delete/<int:exam_id>', methods=['POST'])
@login_required
def delete_exam(exam_id):
    if current_user.role != 'admin':
        return jsonify({'success': False}), 403
    exam = Exam.query.get(exam_id)
    if exam:
        db.session.delete(exam)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/admin/exam/results/<int:exam_id>')
@login_required
def view_exam_results(exam_id):
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    exam = Exam.query.get_or_404(exam_id)
    results = ExamResult.query.filter_by(exam_id=exam_id).all()
    students = Student.query.filter_by(program_id=exam.program_id, semester=exam.semester).all()
    # Build a dict of student_id -> result
    result_dict = {r.student_id: r for r in results}
    return render_template('admin_exam_results.html', exam=exam, students=students, result_dict=result_dict)

@app.route('/admin/exam/results/pdf/<int:exam_id>')
@login_required
def exam_results_pdf(exam_id):
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    exam = Exam.query.get_or_404(exam_id)
    results = ExamResult.query.filter_by(exam_id=exam_id).all()
    students = Student.query.filter_by(program_id=exam.program_id, semester=exam.semester).all()
    result_dict = {r.student_id: r for r in results}
    
    from weasyprint import HTML
    html = render_template('exam_results_pdf.html', exam=exam, students=students, result_dict=result_dict)
    pdf = HTML(string=html).write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=exam_results_{exam.id}.pdf'
    return response

# ------------------------------
# USER MANAGEMENT (Admin)
# ------------------------------
@app.route('/admin/users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    users = User.query.all()
    programs = Program.query.all()
    semesters = ['Semester 1', 'Semester 2', 'Semester 3', 'Semester 4', 'Semester 5', 'Semester 6', 'Semester 7', 'Semester 8']
    return render_template('manage_users.html', users=users, programs=programs, semesters=semesters)

@app.route('/admin/user/add', methods=['POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.form
    if User.query.filter_by(username=data['username']).first():
        flash(f'Username "{data["username"]}" already exists!', 'danger')
        return redirect(url_for('manage_users'))
    if User.query.filter_by(email=data['email']).first():
        flash(f'Email "{data["email"]}" already exists!', 'danger')
        return redirect(url_for('manage_users'))
    try:
        hashed_pw = generate_password_hash(data['password'])
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=hashed_pw,
            role=data['role'],
            full_name=data['full_name']
        )
        db.session.add(user)
        db.session.flush()
        if data['role'] == 'student':
            student = Student(
                user_id=user.id,
                roll_no=data.get('roll_no', ''),
                program_id=data.get('program_id') if data.get('program_id') else None,
                semester=data.get('semester'),
                dob=datetime.strptime(data['dob'], '%Y-%m-%d') if data.get('dob') else None,
                phone=data.get('phone', ''),
                address=data.get('address', ''),
                parent_contact=data.get('parent_contact', '')
            )
            db.session.add(student)
            db.session.flush()
            # Auto-create fee based on program + semester
            fee_obj = ProgramSemesterFee.query.filter_by(program_id=student.program_id, semester=student.semester).first()
            if fee_obj:
                fee = Fee(
                    student_id=student.id,
                    amount=fee_obj.fee_amount,
                    due_date=datetime.utcnow().date() + timedelta(days=30),
                    paid_amount=0,
                    status='Pending',
                    payment_method=None,
                    remarks='Auto-created from program+semester fee'
                )
                db.session.add(fee)
        elif data['role'] == 'faculty':
            faculty = Faculty(
                user_id=user.id,
                department=data.get('department', ''),
                designation=data.get('designation', ''),
                qualification=data.get('qualification', ''),
                joining_date=datetime.strptime(data['joining_date'], '%Y-%m-%d') if data.get('joining_date') else None
            )
            db.session.add(faculty)
        db.session.commit()
        flash('User added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding user: {str(e)}', 'danger')
    return redirect(url_for('manage_users'))

@app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    user = User.query.get(user_id)
    if user:
        if user.role == 'student' and user.student_profile:
            db.session.delete(user.student_profile)
        elif user.role == 'faculty' and user.faculty_profile:
            db.session.delete(user.faculty_profile)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'User deleted'})
    return jsonify({'success': False, 'message': 'User not found'})

@app.route('/admin/user/get/<int:user_id>')
@login_required
def get_user_json(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    user = User.query.get_or_404(user_id)
    result = {
        'id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'email': user.email,
        'role': user.role
    }
    if user.role == 'student' and user.student_profile:
        s = user.student_profile
        result.update({
            'roll_no': s.roll_no,
            'semester': s.semester,
            'program_id': s.program_id,
            'dob': s.dob.strftime('%Y-%m-%d') if s.dob else '',
            'phone': s.phone or '',
            'address': s.address or '',
            'parent_contact': s.parent_contact or ''
        })
    elif user.role == 'faculty' and user.faculty_profile:
        f = user.faculty_profile
        result.update({
            'department': f.department or '',
            'designation': f.designation or '',
            'qualification': f.qualification or '',
            'joining_date': f.joining_date.strftime('%Y-%m-%d') if f.joining_date else ''
        })
    return jsonify(result)

@app.route('/admin/user/edit/<int:user_id>', methods=['POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    user = User.query.get_or_404(user_id)
    data = request.form
    user.full_name = data.get('full_name', user.full_name)
    new_username = data.get('username', '').strip()
    if new_username and new_username != user.username:
        if User.query.filter_by(username=new_username).first():
            flash('Username already taken!', 'danger')
            return redirect(url_for('manage_users'))
        user.username = new_username
    new_password = data.get('new_password', '')
    if new_password and len(new_password) >= 6:
        user.password_hash = generate_password_hash(new_password)
        flash('Password updated!', 'success')
    if user.role == 'student':
        student = Student.query.filter_by(user_id=user.id).first()
        if student:
            student.roll_no = data.get('roll_no', student.roll_no)
            student.semester = data.get('semester', student.semester)
            student.phone = data.get('phone', student.phone)
            student.address = data.get('address', student.address)
            student.parent_contact = data.get('parent_contact', student.parent_contact)
            if data.get('dob'):
                student.dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
            if data.get('program_id'):
                student.program_id = int(data['program_id']) if data['program_id'] else None
    elif user.role == 'faculty':
        faculty = Faculty.query.filter_by(user_id=user.id).first()
        if faculty:
            faculty.department = data.get('department', faculty.department)
            faculty.designation = data.get('designation', faculty.designation)
            faculty.qualification = data.get('qualification', faculty.qualification)
            if data.get('joining_date'):
                faculty.joining_date = datetime.strptime(data['joining_date'], '%Y-%m-%d').date()
    db.session.commit()
    flash('User updated successfully!', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/reset-password-show/<int:user_id>', methods=['POST'])
@login_required
def admin_reset_password_show(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    user = User.query.get_or_404(user_id)
    import random, string
    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({'success': True, 'new_password': new_password, 'username': user.username})

# ------------------------------
# PROGRAM MANAGEMENT (formerly Courses)
# ------------------------------
@app.route('/admin/programs')
@login_required
def manage_programs():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    programs = Program.query.all()
    return render_template('manage_programs.html', programs=programs)

@app.route('/admin/program/add', methods=['POST'])
@login_required
def add_program():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    if Program.query.filter_by(code=request.form['code']).first():
        flash(f'Program code "{request.form["code"]}" already exists!', 'danger')
        return redirect(url_for('manage_programs'))
    program = Program(
        name=request.form['name'],
        code=request.form['code'],
        duration_years=request.form['duration_years'],
        description=request.form.get('description', '')
    )
    db.session.add(program)
    db.session.commit()
    flash('Program added successfully', 'success')
    return redirect(url_for('manage_programs'))

@app.route('/admin/program/delete/<int:program_id>', methods=['POST'])
@login_required
def delete_program(program_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    program = Program.query.get(program_id)
    if program:
        db.session.delete(program)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Program deleted'})
    return jsonify({'success': False, 'message': 'Program not found'})

# ------------------------------
# SUBJECT MANAGEMENT
# ------------------------------
@app.route('/admin/subjects')
@login_required
def manage_subjects():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    subjects = Subject.query.all()
    programs = Program.query.all()
    semesters = ['Semester 1','Semester 2','Semester 3','Semester 4','Semester 5','Semester 6','Semester 7','Semester 8']
    return render_template('manage_subjects.html', subjects=subjects, programs=programs, semesters=semesters)

@app.route('/admin/subject/add', methods=['POST'])
@login_required
def add_subject():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    if Subject.query.filter_by(code=request.form['code']).first():
        flash(f'Subject code "{request.form["code"]}" already exists!', 'danger')
        return redirect(url_for('manage_subjects'))
    subject = Subject(
        program_id=request.form.get('program_id') or None,
        semester=request.form['semester'],
        name=request.form['name'],
        code=request.form['code'],
        credits=request.form['credits'],
        type=request.form['type']
    )
    db.session.add(subject)
    db.session.commit()
    flash('Subject added successfully', 'success')
    return redirect(url_for('manage_subjects'))

@app.route('/admin/subject/get/<int:subject_id>')
@login_required
def get_subject_json(subject_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    subject = Subject.query.get_or_404(subject_id)
    return jsonify({
        'id': subject.id,
        'name': subject.name,
        'code': subject.code,
        'semester': subject.semester,
        'program_id': subject.program_id,
        'credits': subject.credits,
        'type': subject.type
    })

@app.route('/admin/subject/edit/<int:subject_id>', methods=['POST'])
@login_required
def edit_subject(subject_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    subject = Subject.query.get_or_404(subject_id)
    data = request.form
    new_code = data.get('code')
    if new_code and new_code != subject.code:
        if Subject.query.filter_by(code=new_code).first():
            return jsonify({'success': False, 'message': 'Subject code already exists'}), 400
        subject.code = new_code
    subject.name = data.get('name')
    subject.semester = data.get('semester')
    subject.program_id = data.get('program_id') or None
    subject.credits = data.get('credits')
    subject.type = data.get('type')
    db.session.commit()
    return jsonify({'success': True})

# ------------------------------
# FACULTY ASSIGNMENT
# ------------------------------
@app.route('/admin/assign_faculty', methods=['GET', 'POST'])
@login_required
def assign_faculty():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        assignment = FacultyAssignment(
            faculty_id=request.form['faculty_id'],
            subject_id=request.form['subject_id'],
            academic_year=request.form['academic_year']
        )
        db.session.add(assignment)
        db.session.commit()
        flash('Faculty assigned successfully', 'success')
        return redirect(url_for('assign_faculty'))
    faculties = Faculty.query.all()
    subjects = Subject.query.all()
    assignments = FacultyAssignment.query.all()
    return render_template('assign_faculty.html', faculties=faculties, subjects=subjects, assignments=assignments)

@app.route('/admin/faculty-assignment/get/<int:assignment_id>')
@login_required
def get_assignment_json(assignment_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    assignment = FacultyAssignment.query.get_or_404(assignment_id)
    return jsonify({
        'id': assignment.id,
        'faculty_id': assignment.faculty_id,
        'subject_id': assignment.subject_id,
        'academic_year': assignment.academic_year
    })

@app.route('/admin/faculty-assignment/edit/<int:assignment_id>', methods=['POST'])
@login_required
def edit_faculty_assignment(assignment_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    assignment = FacultyAssignment.query.get_or_404(assignment_id)
    data = request.form
    assignment.faculty_id = data.get('faculty_id')
    assignment.subject_id = data.get('subject_id')
    assignment.academic_year = data.get('academic_year')
    db.session.commit()
    return jsonify({'success': True})

# ------------------------------
# TIMETABLE
# ------------------------------
@app.route('/admin/timetable')
@login_required
def manage_timetable():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    programs = Program.query.all()
    faculties = Faculty.query.all()
    subjects = Subject.query.all()
    timetables = Timetable.query.all()
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
    time_slots = ['09:00-10:00','10:00-11:00','11:00-12:00','12:00-13:00','13:00-14:00','14:00-15:00','15:00-16:00','16:00-17:00']
    semesters = ['Semester 1','Semester 2','Semester 3','Semester 4','Semester 5','Semester 6','Semester 7','Semester 8']
    return render_template('manage_timetable.html', programs=programs, faculties=faculties, subjects=subjects,
                           timetables=timetables, days=days, time_slots=time_slots, semesters=semesters)

@app.route('/admin/timetable/add', methods=['POST'])
@login_required
def add_timetable():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    timetable = Timetable(
        program_id=request.form.get('program_id'),
        semester=request.form.get('semester'),
        day=request.form.get('day'),
        time_slot=request.form.get('time_slot'),
        subject_id=request.form.get('subject_id'),
        faculty_id=request.form.get('faculty_id'),
        room_no=request.form.get('room_no')
    )
    db.session.add(timetable)
    db.session.commit()
    flash('Timetable entry added!', 'success')
    return redirect(url_for('manage_timetable'))

@app.route('/admin/timetable/delete/<int:timetable_id>', methods=['POST'])
@login_required
def delete_timetable(timetable_id):
    if current_user.role != 'admin':
        return jsonify({'success': False}), 403
    timetable = Timetable.query.get(timetable_id)
    if timetable:
        db.session.delete(timetable)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

# ------------------------------
# NOTICES
# ------------------------------
@app.route('/admin/notices', methods=['GET', 'POST'])
@login_required
def manage_notices():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        notice = Notice(
            title=request.form['title'],
            content=request.form['content'],
            audience=request.form['audience'],
            created_by=current_user.id
        )
        db.session.add(notice)
        db.session.commit()
        flash('Notice posted successfully', 'success')
        return redirect(url_for('manage_notices'))
    notices = Notice.query.order_by(Notice.created_at.desc()).all()
    return render_template('manage_notices.html', notices=notices)

@app.route('/admin/notice/delete/<int:notice_id>', methods=['POST'])
@login_required
def delete_notice(notice_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    notice = Notice.query.get(notice_id)
    if notice:
        db.session.delete(notice)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Notice deleted'})
    return jsonify({'success': False, 'message': 'Notice not found'})

# ------------------------------
# NOTIFICATIONS
# ------------------------------
@app.route('/admin/notifications-page')
@login_required
def manage_notifications_page():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    sent_notifications = Notification.query.filter_by(created_by=current_user.id).order_by(Notification.created_at.desc()).all()
    students = User.query.filter_by(role='student').all()
    faculty = User.query.filter_by(role='faculty').all()
    return render_template('manage_notifications.html', sent_notifications=sent_notifications, students=students, faculty=faculty)

@app.route('/admin/notification/send', methods=['POST'])
@login_required
def send_notification():
    if current_user.role != 'admin':
        return jsonify({'success': False}), 403
    notification = Notification(
        title=request.form.get('title'),
        message=request.form.get('message'),
        notification_type=request.form.get('notification_type', 'general'),
        audience=request.form.get('audience'),
        specific_user_id=request.form.get('specific_user_id') or None,
        created_by=current_user.id,
        expiry_date=datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d').date() if request.form.get('expiry_date') else None
    )
    db.session.add(notification)
    db.session.commit()
    flash('Notification sent!', 'success')
    return redirect(url_for('manage_notifications_page'))

@app.route('/admin/notification/delete/<int:notification_id>', methods=['POST'])
@login_required
def delete_notification(notification_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    notification = Notification.query.get(notification_id)
    if notification and notification.created_by == current_user.id:
        db.session.delete(notification)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Notification deleted'})
    return jsonify({'success': False, 'message': 'Notification not found'})

@app.route('/api/notifications/unread')
@login_required
def get_unread_notifications():
    notifications = Notification.query.filter(
        ((Notification.audience == 'all') | (Notification.audience == current_user.role) |
         (Notification.specific_user_id == current_user.id)) & (Notification.is_read == False)
    ).order_by(Notification.created_at.desc()).limit(10).all()
    return jsonify([{
        'id': n.id, 'title': n.title,
        'message': n.message[:100] + '...' if len(n.message) > 100 else n.message,
        'type': n.notification_type,
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M')
    } for n in notifications])

@app.route('/api/notification/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get(notification_id)
    if notification:
        notification.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

# ------------------------------
# FEE MANAGEMENT
# ------------------------------

@app.route('/admin/program-semester-fee/add', methods=['POST'])
@login_required
def add_program_semester_fee():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    
    program_id = request.form.get('program_id')
    semester = request.form.get('semester')
    amount_str = request.form.get('fee_amount')
    
    if not program_id or not semester or not amount_str:
        flash('All fields are required!', 'danger')
        return redirect(url_for('manage_program_semester_fees'))
    
    try:
        amount = float(amount_str)
    except ValueError:
        flash('Invalid fee amount', 'danger')
        return redirect(url_for('manage_program_semester_fees'))
    
    # Get program to safely display name
    program = Program.query.get(program_id)
    if not program:
        flash('Selected program does not exist.', 'danger')
        return redirect(url_for('manage_program_semester_fees'))
    
    existing = ProgramSemesterFee.query.filter_by(program_id=program_id, semester=semester).first()
    if existing:
        existing.fee_amount = amount
        existing.academic_year = ACADEMIC_YEAR
        db.session.commit()
        flash(f'✅ Updated fee for {program.name} - {semester} to ₹{amount:.2f}', 'success')
    else:
        new_fee = ProgramSemesterFee(
            program_id=program_id,
            semester=semester,
            fee_amount=amount,
            academic_year=ACADEMIC_YEAR
        )
        db.session.add(new_fee)
        db.session.commit()
        flash(f'✅ Added fee for {program.name} - {semester}: ₹{amount:.2f}', 'success')
    
    return redirect(url_for('manage_program_semester_fees'))

@app.route('/admin/manage-fees')
@login_required
def admin_manage_fees():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    students = Student.query.all()
    fee_data = []
    total_fees = total_paid = pending_count = 0
    for student in students:
        fee = Fee.query.filter_by(student_id=student.id).order_by(Fee.due_date.desc()).first()
        if fee:
            fee_data.append({'student': student, 'fee': fee})
            total_fees += fee.amount
            total_paid += fee.paid_amount
            if fee.status != 'Paid':
                pending_count += 1
    total_due = total_fees - total_paid
    default_message = f"Dear Student, your college fee is pending. Please pay at the earliest. - {COLLEGE_NAME}"
    return render_template('admin_fees.html', fee_data=fee_data, total_fees=total_fees, total_paid=total_paid,
                          total_due=total_due, pending_count=pending_count, default_message=default_message)

@app.route('/admin/add-fee', methods=['GET', 'POST'])
@login_required
def add_fee():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        amount = float(request.form.get('amount'))
        due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date()
        new_fee = Fee(
            student_id=student_id,
            amount=amount,
            due_date=due_date,
            paid_amount=0,
            status='Pending',
            payment_method=None,
            remarks='Manual fee record'
        )
        db.session.add(new_fee)
        db.session.commit()
        flash('Fee record added successfully!', 'success')
        return redirect(url_for('admin_manage_fees'))
    students = Student.query.all()
    return render_template('add_fee.html', students=students)

@app.route('/admin/record-payment', methods=['POST'])
@login_required
def record_payment():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    fee_id = request.form.get('fee_id')
    payment_amount = float(request.form.get('payment_amount', 0))
    payment_method = request.form.get('payment_method', 'Cash')
    transaction_id = request.form.get('transaction_id', '')
    remarks = request.form.get('remarks', '')
    fee = Fee.query.get(fee_id)
    if not fee:
        flash('Fee record not found!', 'danger')
        return redirect(url_for('admin_manage_fees'))
    if payment_amount <= 0:
        flash('Payment amount must be greater than zero.', 'danger')
        return redirect(url_for('admin_manage_fees'))
    fee.paid_amount += payment_amount
    fee.status = 'Paid' if fee.paid_amount >= fee.amount else 'Partial'
    fee.payment_date = datetime.utcnow()
    fee.payment_method = payment_method
    fee.remarks = remarks
    if transaction_id:
        fee.transaction_id = transaction_id
    db.session.commit()
    flash('Payment recorded successfully!', 'success')
    return redirect(url_for('admin_manage_fees'))

@app.route('/admin/program-semester-fees')
@login_required
def manage_program_semester_fees():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    from models import ProgramSemesterFee, Program
    fees = ProgramSemesterFee.query.all()
    programs = Program.query.all()
    semesters = ['Semester 1','Semester 2','Semester 3','Semester 4','Semester 5','Semester 6','Semester 7','Semester 8']
    return render_template('manage_program_semester_fees.html', fees=fees, programs=programs, semesters=semesters)

# ------------------------------
# STUDENT PROMOTION (Semester)
# ------------------------------
@app.route('/admin/promote-students', methods=['GET', 'POST'])
@login_required
def promote_students():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    # Get current semester distribution
    semesters = ['Semester 1','Semester 2','Semester 3','Semester 4','Semester 5','Semester 6','Semester 7','Semester 8']
    semester_counts = {}
    for sem in semesters:
        semester_counts[sem] = Student.query.filter_by(semester=sem).count()
    if request.method == 'POST':
        promotions = {}
        for key, value in request.form.items():
            if key.startswith('promote_') and value:
                source_sem = key.replace('promote_', '')
                promotions[source_sem] = value
        promoted_count = 0
        for source, target in promotions.items():
            students = Student.query.filter_by(semester=source).all()
            for student in students:
                student.semester = target
                promoted_count += 1
        db.session.commit()
        flash(f'{promoted_count} students promoted to next semester!', 'success')
        return redirect(url_for('promote_students'))
    return render_template('admin_promote_students.html', semesters=semesters, semester_counts=semester_counts)

# ------------------------------
# ATTENDANCE (Faculty)
# ------------------------------
@app.route('/faculty/attendance', methods=['GET', 'POST'])
@login_required
def mark_attendance():
    if current_user.role != 'faculty':
        return redirect(url_for('login'))
    faculty = Faculty.query.filter_by(user_id=current_user.id).first()
    assignments = FacultyAssignment.query.filter_by(faculty_id=faculty.id).all() if faculty else []
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        subject = Subject.query.get(subject_id)
        students = Student.query.filter_by(program_id=subject.program_id, semester=subject.semester).all()
        for student in students:
            status = request.form.get('status_' + str(student.id), 'Absent')
            attendance = Attendance.query.filter_by(student_id=student.id, subject_id=subject_id, date=date).first()
            if not attendance:
                attendance = Attendance(student_id=student.id, subject_id=subject_id, date=date, status=status)
                db.session.add(attendance)
        db.session.commit()
        flash('Attendance marked successfully', 'success')
        return redirect(url_for('mark_attendance'))
    return render_template('attendance.html', assignments=assignments, today=datetime.utcnow().date())

# ------------------------------
# MARKS ENTRY (Faculty)
# ------------------------------
@app.route('/faculty/marks', methods=['GET', 'POST'])
@login_required
def enter_marks():
    if current_user.role != 'faculty':
        return redirect(url_for('login'))
    faculty = Faculty.query.filter_by(user_id=current_user.id).first()
    assignments = FacultyAssignment.query.filter_by(faculty_id=faculty.id).all() if faculty else []
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        exam_type = request.form['exam_type']
        max_marks = int(request.form['max_marks'])
        subject = Subject.query.get(subject_id)
        students = Student.query.filter_by(program_id=subject.program_id, semester=subject.semester).all()
        for student in students:
            obtained = request.form.get('marks_' + str(student.id))
            if obtained:
                marks = Marks.query.filter_by(student_id=student.id, subject_id=subject_id, exam_type=exam_type).first()
                if not marks:
                    marks = Marks(student_id=student.id, subject_id=subject_id, exam_type=exam_type, max_marks=max_marks, obtained_marks=float(obtained))
                    db.session.add(marks)
                else:
                    marks.obtained_marks = float(obtained)
        db.session.commit()
        flash('Marks saved successfully', 'success')
        return redirect(url_for('enter_marks'))
    return render_template('marks_entry.html', assignments=assignments)

# ------------------------------
# ATTENDANCE REPORT (Admin)
# ------------------------------
@app.route('/admin/attendance-report')
@login_required
def admin_attendance_report():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    programs = Program.query.all()
    subjects = Subject.query.all()
    semesters = ['Semester 1','Semester 2','Semester 3','Semester 4','Semester 5','Semester 6','Semester 7','Semester 8']
    selected_program = request.args.get('program_id', type=int)
    selected_semester = request.args.get('semester')
    selected_subject = request.args.get('subject_id', type=int)
    students_data = []
    if selected_program and selected_semester:
        student_list = Student.query.filter_by(program_id=selected_program, semester=selected_semester).all()
        for student in student_list:
            att_query = Attendance.query.filter_by(student_id=student.id)
            if selected_subject:
                att_query = att_query.filter_by(subject_id=selected_subject)
            records = att_query.all()
            total = len(records)
            present = sum(1 for r in records if r.status == 'Present')
            percent = (present / total * 100) if total > 0 else 0
            students_data.append({
                'student': student,
                'total': total,
                'present': present,
                'absent': total - present,
                'percent': round(percent, 1)
            })
    selected_program_obj = Program.query.get(selected_program) if selected_program else None
    return render_template('admin_attendance_report.html', programs=programs, subjects=subjects,
                           semesters=semesters, selected_program=selected_program, selected_semester=selected_semester,
                           selected_subject=selected_subject, selected_program_obj=selected_program_obj,
                           students=students_data)

@app.route('/api/student-subject-attendance/<int:student_id>')
@login_required
def student_subject_attendance(student_id):
    if current_user.role not in ['admin', 'faculty']:
        return jsonify({'error': 'Unauthorized'}), 403
    student = Student.query.get_or_404(student_id)
    subjects_with_attendance = db.session.query(Attendance.subject_id).filter_by(student_id=student.id).distinct().all()
    subject_ids = [s[0] for s in subjects_with_attendance]
    subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all()
    result = []
    for sub in subjects:
        records = Attendance.query.filter_by(student_id=student.id, subject_id=sub.id).all()
        total = len(records)
        present = sum(1 for r in records if r.status == 'Present')
        absent = total - present
        result.append({
            'subject_name': f"{sub.name} ({sub.code})",
            'total': total,
            'present': present,
            'absent': absent,
        })
    return jsonify(result)

# ------------------------------
# MARKS VIEW (Admin)
# ------------------------------
@app.route('/admin/view-marks')
@login_required
def admin_view_marks():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    programs = Program.query.all()
    semesters = ['Semester 1','Semester 2','Semester 3','Semester 4','Semester 5','Semester 6','Semester 7','Semester 8']
    exam_types = ['Mid Semester', 'End Semester', 'Practical', 'Internal Assessment']
    selected_program = request.args.get('program_id', type=int)
    selected_semester = request.args.get('semester')
    selected_exam = request.args.get('exam_type', 'End Semester')
    students_data = []
    subjects = []
    if selected_program and selected_semester:
        subjects = Subject.query.filter_by(program_id=selected_program, semester=selected_semester).all()
        students = Student.query.filter_by(program_id=selected_program, semester=selected_semester).all()
        for student in students:
            student_marks = {}
            for subject in subjects:
                mark = Marks.query.filter_by(student_id=student.id, subject_id=subject.id, exam_type=selected_exam).first()
                student_marks[subject.id] = {
                    'obtained': mark.obtained_marks if mark else '-',
                    'max': mark.max_marks if mark else '-'
                }
            students_data.append({'student': student, 'marks': student_marks})
    return render_template('admin_view_marks.html', programs=programs, semesters=semesters,
                           exam_types=exam_types, selected_program=selected_program, selected_semester=selected_semester,
                           selected_exam=selected_exam, subjects=subjects, students_data=students_data)

# ------------------------------
# FACULTY & STUDENT DASHBOARDS
# ------------------------------
@app.route('/faculty/dashboard')
@login_required
def faculty_dashboard():
    if current_user.role != 'faculty':
        return redirect(url_for('login'))
    faculty = Faculty.query.filter_by(user_id=current_user.id).first()
    assignments = FacultyAssignment.query.filter_by(faculty_id=faculty.id).all() if faculty else []
    return render_template('faculty_dashboard.html', faculty=faculty, assignments=assignments)

@app.route('/faculty/timetable')
@login_required
def faculty_timetable():
    if current_user.role != 'faculty':
        return redirect(url_for('login'))
    faculty = Faculty.query.filter_by(user_id=current_user.id).first()
    timetables = Timetable.query.filter_by(faculty_id=faculty.id).all() if faculty else []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    time_slots = ['09:00-10:00','10:00-11:00','11:00-12:00','12:00-13:00','13:00-14:00','14:00-15:00','15:00-16:00','16:00-17:00']
    return render_template('faculty_timetable.html', timetables=timetables, days=days, time_slots=time_slots)

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        return redirect(url_for('login'))
    student = Student.query.filter_by(user_id=current_user.id).first()
    attendance_percent = 0
    present = 0
    total_classes = 0
    recent_marks = []
    fee = None
    notices = []
    if student:
        attendance_records = Attendance.query.filter_by(student_id=student.id).all()
        total_classes = len(attendance_records)
        present = sum(1 for a in attendance_records if a.status == 'Present')
        attendance_percent = (present / total_classes * 100) if total_classes > 0 else 0
        recent_marks = Marks.query.filter_by(student_id=student.id).order_by(Marks.id.desc()).limit(5).all()
        fee = Fee.query.filter_by(student_id=student.id).order_by(Fee.due_date.desc()).first()
        notices = Notice.query.filter(Notice.audience.in_(['all', 'students'])).order_by(Notice.created_at.desc()).limit(5).all()
    return render_template('student_dashboard.html', student=student,
                           attendance_percent=attendance_percent, present=present, total_classes=total_classes,
                           recent_marks=recent_marks, fee=fee, notices=notices)

@app.route('/student/attendance')
@login_required
def view_attendance():
    if current_user.role != 'student':
        return redirect(url_for('login'))
    student = Student.query.filter_by(user_id=current_user.id).first()
    attendance = []
    if student:
        attendance = db.session.query(Attendance, Subject).join(Subject).filter(Attendance.student_id == student.id).all()
    return render_template('student_attendance.html', attendance=attendance)

@app.route('/student/marks')
@login_required
def view_marks():
    if current_user.role != 'student':
        return redirect(url_for('login'))
    student = Student.query.filter_by(user_id=current_user.id).first()
    marks = []
    if student:
        marks = db.session.query(Marks, Subject).join(Subject).filter(Marks.student_id == student.id).all()
    return render_template('student_marks.html', marks=marks)

@app.route('/student/fees')
@login_required
def view_fees():
    if current_user.role != 'student':
        return redirect(url_for('login'))
    student = Student.query.filter_by(user_id=current_user.id).first()
    fees = []
    if student:
        fees = Fee.query.filter_by(student_id=student.id).all()
    return render_template('student_fees.html', fees=fees)

@app.route('/student/timetable')
@login_required
def student_timetable():
    if current_user.role != 'student':
        return redirect(url_for('login'))
    student = Student.query.filter_by(user_id=current_user.id).first()
    timetables = Timetable.query.filter_by(program_id=student.program_id, semester=student.semester).all() if student else []
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
    time_slots = ['09:00-10:00','10:00-11:00','11:00-12:00','12:00-13:00','13:00-14:00','14:00-15:00','15:00-16:00','16:00-17:00']
    return render_template('student_timetable.html', timetables=timetables, days=days, time_slots=time_slots)

# ------------------------------
# ID CARD & QR
# ------------------------------
@app.route('/student/id-card')
@login_required
def student_id_card():
    if current_user.role != 'student':
        return redirect(url_for('login'))
    student = Student.query.filter_by(user_id=current_user.id).first()
    return render_template('student_id_card.html', student=student)

@app.route('/student/qrcode/<roll_no>')
@login_required
def generate_qr(roll_no):
    college_website = "https://risecollege.edu.in"  # Replace with actual domain
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(college_website)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

# ------------------------------
# ONLINE ADMISSION (PUBLIC)
# ------------------------------
class AdmissionApplication(db.Model):
    __tablename__ = 'admission_applications'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100))
    mother_name = db.Column(db.String(100))
    dob = db.Column(db.Date)
    gender = db.Column(db.String(10))
    applying_program_id = db.Column(db.Integer, db.ForeignKey('programs.id'))
    semester = db.Column(db.String(50), default='Semester 1')
    phone = db.Column(db.String(15))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    previous_institution = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)

@app.route('/admission', methods=['GET', 'POST'])
def admission_form():
    programs = Program.query.all()
    if request.method == 'POST':
        try:
            application = AdmissionApplication(
                full_name=request.form.get('full_name'),
                father_name=request.form.get('father_name'),
                mother_name=request.form.get('mother_name'),
                dob=datetime.strptime(request.form.get('dob'), '%Y-%m-%d') if request.form.get('dob') else None,
                gender=request.form.get('gender'),
                applying_program_id=request.form.get('applying_program_id'),
                semester='Semester 1',
                phone=request.form.get('phone'),
                email=request.form.get('email'),
                address=request.form.get('address'),
                previous_institution=request.form.get('previous_institution'),
                status='pending'
            )
            db.session.add(application)
            db.session.commit()
            flash('Admission form submitted successfully! We will contact you soon.', 'success')
            return redirect(url_for('admission_form'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    return render_template('admission_form.html', programs=programs)

@app.route('/admin/admissions')
@login_required
def admin_admissions():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    status_filter = request.args.get('status', 'pending')
    applications = AdmissionApplication.query.filter_by(status=status_filter).order_by(AdmissionApplication.created_at.desc()).all()
    statuses = ['pending', 'approved', 'rejected']
    return render_template('admin_admissions.html', applications=applications, current_status=status_filter, statuses=statuses)

@app.route('/admin/admission/approve/<int:app_id>', methods=['POST'])
@login_required
def approve_admission(app_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    application = AdmissionApplication.query.get_or_404(app_id)
    application.status = 'approved'
    application.approved_at = datetime.utcnow()
    application.remarks = request.form.get('remarks', '')
    db.session.commit()
    # Auto-create student account
    try:
        base_username = application.full_name.lower().replace(' ', '_')[:20]
        username = base_username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1
        password = f"admission{application.id}"
        hashed = generate_password_hash(password)
        user = User(
            username=username,
            email=application.email or f"{username}@college.edu",
            password_hash=hashed,
            role='student',
            full_name=application.full_name
        )
        db.session.add(user)
        db.session.flush()
        roll_no = f"ADM{datetime.utcnow().year}{application.id:04d}"
        student = Student(
            user_id=user.id,
            roll_no=roll_no,
            program_id=application.applying_program_id,
            semester=application.semester,
            dob=application.dob,
            phone=application.phone,
            address=application.address,
            parent_contact=application.father_name or application.mother_name
        )
        db.session.add(student)
        db.session.commit()
    except Exception as e:
        print(f"Error creating student: {e}")
    return jsonify({'success': True})

@app.route('/admin/admission/reject/<int:app_id>', methods=['POST'])
@login_required
def reject_admission(app_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    application = AdmissionApplication.query.get_or_404(app_id)
    application.status = 'rejected'
    application.remarks = request.form.get('remarks', '')
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/admission/delete/<int:app_id>', methods=['POST'])
@login_required
def delete_admission(app_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    application = AdmissionApplication.query.get_or_404(app_id)
    db.session.delete(application)
    db.session.commit()
    return jsonify({'success': True})

# ------------------------------
# PROFILE & SETTINGS
# ------------------------------
@app.route('/profile')
@login_required
def profile():
    user = current_user
    student = Student.query.filter_by(user_id=user.id).first() if user.role == 'student' else None
    faculty = Faculty.query.filter_by(user_id=user.id).first() if user.role == 'faculty' else None
    return render_template('profile.html', user=user, student=student, faculty=faculty)

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    user = current_user
    data = request.form
    user.full_name = data.get('full_name', user.full_name)
    if user.role == 'student':
        student = Student.query.filter_by(user_id=user.id).first()
        if student:
            student.phone = data.get('phone', student.phone)
            student.address = data.get('address', student.address)
            student.parent_contact = data.get('parent_contact', student.parent_contact)
    elif user.role == 'faculty':
        faculty = Faculty.query.filter_by(user_id=user.id).first()
        if faculty:
            faculty.department = data.get('department', faculty.department)
            faculty.designation = data.get('designation', faculty.designation)
            faculty.qualification = data.get('qualification', faculty.qualification)
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/change-username', methods=['POST'])
@login_required
def change_username():
    new_username = request.form.get('new_username', '').strip()
    password = request.form.get('password', '')
    if not new_username:
        flash('Username cannot be empty.', 'danger')
        return redirect(url_for('profile'))
    if not check_password_hash(current_user.password_hash, password):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('profile'))
    if User.query.filter_by(username=new_username).first():
        flash('Username already taken. Please choose another.', 'danger')
        return redirect(url_for('profile'))
    current_user.username = new_username
    db.session.commit()
    flash('Username changed successfully! Please log in again.', 'success')
    logout_user()
    return redirect(url_for('login'))

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    if not check_password_hash(current_user.password_hash, current_password):
        flash('Current password is incorrect!', 'danger')
    elif new_password != confirm_password:
        flash('New passwords do not match!', 'danger')
    elif len(new_password) < 6:
        flash('Password must be at least 6 characters!', 'danger')
    else:
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash('Password changed successfully! Please log in again.', 'success')
        logout_user()
        return redirect(url_for('login'))
    return redirect(url_for('profile'))

@app.route('/upload_profile_pic', methods=['POST'])
@login_required
def upload_profile_pic():
    if 'profile_pic' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('profile'))
    file = request.files['profile_pic']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('profile'))
    if file and allowed_file(file.filename):
        try:
            upload_result = cloudinary.uploader.upload(file, folder="college_profiles",
                                                       public_id=f"user_{current_user.id}", overwrite=True, resource_type="image")
            current_user.profile_pic = upload_result['secure_url']
            db.session.commit()
            flash('Profile picture updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error uploading to Cloudinary: {str(e)}', 'danger')
    else:
        flash('Invalid file type. Allowed: png, jpg, jpeg, gif, webp', 'danger')
    return redirect(url_for('profile'))

# ------------------------------
# SMS ROUTES
# ------------------------------
@app.route('/api/get_students_by_subject/<int:subject_id>')
@login_required
def get_students_by_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    students = Student.query.filter_by(program_id=subject.program_id, semester=subject.semester).all()
    result = []
    for s in students:
        result.append({
            'id': s.id,
            'roll_no': s.roll_no,
            'name': s.user.full_name if s.user else f"Student {s.id}",
            'phone': s.phone or ''
        })
    return jsonify(result)

@app.route('/admin/send-sms')
@login_required
def send_sms_page():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    return render_template('send_sms.html')

@app.route('/admin/bulk-sms', methods=['POST'])
@login_required
def bulk_sms():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    audience = request.form.get('audience')
    message = request.form.get('message')
    if audience == 'all_students':
        students = Student.query.all()
    elif audience == 'due_fees':
        students = db.session.query(Student).join(Fee).filter(Fee.status != 'Paid').all()
    else:
        students = []
    success_count = 0
    for student in students:
        if student.phone:
            success, _ = send_sms(student.phone, message)
            if success:
                success_count += 1
    flash(f'SMS sent to {success_count} students!', 'success' if success_count > 0 else 'info')
    return redirect(url_for('send_sms_page'))

@app.route('/admin/send-fee-reminder/<int:student_id>')
@login_required
def send_fee_reminder(student_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    student = Student.query.get(student_id)
    if student and student.phone:
        fee = Fee.query.filter_by(student_id=student_id).filter(Fee.status != 'Paid').first()
        if fee:
            due = fee.amount - fee.paid_amount
            message = f"Dear {student.user.full_name}, your college fee of Rs.{due:.2f} is pending. Due date: {fee.due_date}. - {COLLEGE_NAME}"
            success, sid = send_sms(student.phone, message)
            flash('SMS sent!' if success else f'Failed: {sid}', 'success' if success else 'danger')
    return redirect(url_for('admin_manage_fees'))

# ------------------------------
# DATABASE SETUP
# ------------------------------
@app.route('/setup-db')
def setup_db():
    try:
        db.drop_all()
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@risecollege.edu.in', password_hash=generate_password_hash('admin123'), role='admin', full_name='College Administrator')
            db.session.add(admin)
            db.session.commit()
        if Program.query.count() == 0:
            programs = [
                Program(name='Bachelor of Computer Applications', code='BCA', duration_years=3, description='Computer Applications'),
                Program(name='Bachelor of Business Administration', code='BBA', duration_years=3, description='Business Administration'),
                Program(name='Bachelor of Science (CS)', code='BSC-CS', duration_years=3, description='Computer Science')
            ]
            db.session.add_all(programs)
            db.session.commit()
        if not User.query.filter_by(username='faculty1').first():
            faculty_user = User(username='faculty1', email='faculty@college.edu', password_hash=generate_password_hash('pass123'), role='faculty', full_name='Dr. John Smith')
            db.session.add(faculty_user)
            db.session.commit()
            db.session.add(Faculty(user_id=faculty_user.id, department='Computer Science', designation='Professor', qualification='Ph.D.', joining_date=datetime.utcnow().date()))
            db.session.commit()
        if not User.query.filter_by(username='student1').first():
            student_user = User(username='student1', email='student@college.edu', password_hash=generate_password_hash('pass123'), role='student', full_name='Alice Johnson')
            db.session.add(student_user)
            db.session.commit()
            student = Student(user_id=student_user.id, roll_no='R2024001', program_id=1, semester='Semester 1', dob=datetime(2005,5,15).date(), phone='+919876543210', address='Chapra, Bihar')
            db.session.add(student)
            db.session.commit()
            db.session.add(Fee(student_id=student.id, amount=50000, due_date=datetime.utcnow().date()+timedelta(days=30), paid_amount=25000, status='Partial'))
            db.session.commit()
        return "✅ Database setup complete!<br><br>Admin: admin / admin123<br>Faculty: faculty1 / pass123<br>Student: student1 / pass123<br><br><a href='/login'>Login</a>"
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email=COLLEGE_EMAIL, password_hash=generate_password_hash('admin123'), role='admin', full_name='College Administrator')
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin created")
        if Program.query.count() == 0:
            default_programs = [
                Program(name='Bachelor of Computer Applications', code='BCA', duration_years=3, description='Computer Applications'),
                Program(name='Bachelor of Business Administration', code='BBA', duration_years=3, description='Business Administration'),
                Program(name='Bachelor of Science (CS)', code='BSC-CS', duration_years=3, description='Computer Science')
            ]
            db.session.add_all(default_programs)
            db.session.commit()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)