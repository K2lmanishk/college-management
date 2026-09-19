from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import User, Student, Faculty, Program
from .forms import LoginForm

SEMESTERS = [f'Semester {i}' for i in range(1, 9)]


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    role = request.user.role
    if role == 'admin':
        return admin_dashboard(request)
    if role == 'faculty':
        return faculty_dashboard(request)
    return student_dashboard(request)


def admin_dashboard(request):
    ctx = {
        'total_students': Student.objects.count(),
        'total_faculty': Faculty.objects.count(),
        'total_programs': Program.objects.count(),
    }
    return render(request, 'dashboard_admin.html', ctx)


def faculty_dashboard(request):
    faculty = getattr(request.user, 'faculty_profile', None)
    assignments = faculty.assignments.select_related('subject__program') if faculty else []
    return render(request, 'dashboard_faculty.html', {'faculty': faculty, 'assignments': assignments})


def student_dashboard(request):
    student = getattr(request.user, 'student_profile', None)
    return render(request, 'dashboard_student.html', {'student': student})


@login_required
def manage_users(request):
    if request.user.role != 'admin':
        return redirect('dashboard')
    users = User.objects.all().order_by('-id')
    return render(request, 'manage_users.html', {
        'users': users,
        'programs': Program.objects.all(),
        'semesters': SEMESTERS,
    })


@login_required
@require_POST
def add_user(request):
    if request.user.role != 'admin':
        return redirect('dashboard')
    data = request.POST
    username = data.get('username', '').strip()
    role = data.get('role', 'student')
    if not username or not data.get('password'):
        messages.error(request, 'Username and password are required')
        return redirect('manage_users')
    if User.objects.filter(username=username).exists():
        messages.error(request, 'Username already exists')
        return redirect('manage_users')
    if role == 'student':
        roll_no = data.get('roll_no', '').strip()
        if not roll_no or Student.objects.filter(roll_no=roll_no).exists():
            messages.error(request, 'A unique roll number is required for students')
            return redirect('manage_users')
    user = User.objects.create_user(
        username=username, email=data.get('email', ''),
        password=data['password'], role=role,
        full_name=data.get('full_name', ''),
    )
    if role == 'student':
        Student.objects.create(
            user=user, roll_no=data['roll_no'].strip(),
            program_id=data.get('program_id') or None,
            semester=data.get('semester', ''),
        )
    elif role == 'faculty':
        Faculty.objects.create(user=user)
    messages.success(request, 'User added successfully')
    return redirect('manage_users')


@login_required
@require_POST
def delete_user(request, user_id):
    if request.user.role != 'admin':
        return JsonResponse({'success': False}, status=403)
    if request.user.id == user_id:
        return JsonResponse({'success': False, 'error': 'You cannot delete yourself'}, status=400)
    User.objects.filter(id=user_id).delete()
    return JsonResponse({'success': True})


@login_required
def profile(request):
    return render(request, 'profile.html')


@login_required
@require_POST
def update_profile(request):
    user = request.user
    user.full_name = request.POST.get('full_name', user.full_name)
    user.email = request.POST.get('email', user.email)
    if request.FILES.get('profile_pic'):
        user.profile_pic = request.FILES['profile_pic']
    user.save()
    messages.success(request, 'Profile updated')
    return redirect('profile')
