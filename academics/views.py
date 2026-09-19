from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import Subject, FacultyAssignment, Attendance, Marks
from accounts.models import Student, Program

SEMESTERS = [f'Semester {i}' for i in range(1, 9)]


def _faculty_assignments(user):
    faculty = getattr(user, 'faculty_profile', None)
    if not faculty:
        return FacultyAssignment.objects.none()
    return FacultyAssignment.objects.filter(faculty=faculty).select_related('subject')


@login_required
def manage_subjects(request):
    if request.user.role != 'admin':
        return redirect('dashboard')
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        if Subject.objects.filter(code=code).exists():
            messages.error(request, 'A subject with that code already exists')
            return redirect('manage_subjects')
        Subject.objects.create(
            program_id=request.POST.get('program_id') or None,
            semester=request.POST.get('semester', ''),
            name=request.POST.get('name', ''),
            code=code,
            credits=request.POST.get('credits') or 3,
            type=request.POST.get('type', 'Theory'),
        )
        messages.success(request, 'Subject added')
        return redirect('manage_subjects')
    return render(request, 'manage_subjects.html', {
        'subjects': Subject.objects.select_related('program'),
        'programs': Program.objects.all(),
        'semesters': SEMESTERS,
    })


@login_required
def mark_attendance(request):
    if request.user.role != 'faculty':
        return redirect('dashboard')
    assignments = _faculty_assignments(request.user)
    if request.method == 'POST':
        subject = get_object_or_404(Subject, id=request.POST['subject_id'])
        if not assignments.filter(subject=subject).exists():
            messages.error(request, 'You are not assigned to that subject')
            return redirect('mark_attendance')
        date = request.POST['date']
        students = Student.objects.filter(program=subject.program, semester=subject.semester)
        for s in students:
            status = request.POST.get(f'status_{s.id}', 'Absent')
            Attendance.objects.update_or_create(
                student=s, subject=subject, date=date,
                defaults={'status': status},
            )
        messages.success(request, 'Attendance saved')
        return redirect('mark_attendance')
    return render(request, 'attendance.html', {'assignments': assignments})


@login_required
def enter_marks(request):
    if request.user.role != 'faculty':
        return redirect('dashboard')
    assignments = _faculty_assignments(request.user)
    if request.method == 'POST':
        subject = get_object_or_404(Subject, id=request.POST['subject_id'])
        if not assignments.filter(subject=subject).exists():
            messages.error(request, 'You are not assigned to that subject')
            return redirect('enter_marks')
        exam_type = request.POST['exam_type']
        max_marks = int(request.POST['max_marks'])
        students = Student.objects.filter(program=subject.program, semester=subject.semester)
        for s in students:
            val = request.POST.get(f'marks_{s.id}')
            if val:
                Marks.objects.update_or_create(
                    student=s, subject=subject, exam_type=exam_type,
                    defaults={'max_marks': max_marks, 'obtained_marks': float(val)},
                )
        messages.success(request, 'Marks saved')
        return redirect('enter_marks')
    return render(request, 'marks_entry.html', {'assignments': assignments})


@login_required
def get_students_by_subject(request, subject_id):
    if request.user.role not in ('faculty', 'admin'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    subject = get_object_or_404(Subject, id=subject_id)
    students = Student.objects.filter(
        program=subject.program, semester=subject.semester
    ).select_related('user')
    return JsonResponse([{
        'id': s.id, 'roll_no': s.roll_no,
        'name': s.user.full_name or s.user.username, 'phone': s.phone or '',
    } for s in students], safe=False)


@login_required
def student_attendance(request):
    if request.user.role != 'student':
        return redirect('dashboard')
    student = getattr(request.user, 'student_profile', None)
    att = Attendance.objects.filter(student=student).select_related('subject').order_by('-date') if student else []
    total = len(att)
    present = sum(1 for a in att if a.status == 'Present')
    pct = round(present * 100 / total, 1) if total else 0
    return render(request, 'student_attendance.html', {'attendance': att, 'percentage': pct, 'total': total, 'present': present})


@login_required
def student_marks(request):
    if request.user.role != 'student':
        return redirect('dashboard')
    student = getattr(request.user, 'student_profile', None)
    marks = Marks.objects.filter(student=student).select_related('subject') if student else []
    return render(request, 'student_marks.html', {'marks': marks})
