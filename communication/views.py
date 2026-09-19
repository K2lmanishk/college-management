from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Notice, Notification, AdmissionApplication
from accounts.models import Program


@login_required
def manage_notices(request):
    if request.user.role != 'admin':
        return redirect('dashboard')
    if request.method == 'POST':
        Notice.objects.create(
            title=request.POST['title'], content=request.POST['content'],
            audience=request.POST.get('audience', 'all'), created_by=request.user,
        )
        messages.success(request, 'Notice posted')
        return redirect('manage_notices')
    return render(request, 'manage_notices.html', {'notices': Notice.objects.all()})


@login_required
@require_POST
def delete_notice(request, notice_id):
    if request.user.role != 'admin':
        return JsonResponse({'success': False}, status=403)
    Notice.objects.filter(id=notice_id).delete()
    return JsonResponse({'success': True})


@login_required
def unread_notifications_api(request):
    notifs = Notification.objects.filter(is_read=False).filter(
        Q(audience='all') | Q(audience=request.user.role) | Q(specific_user=request.user)
    )[:10]
    return JsonResponse([{
        'id': n.id, 'title': n.title, 'message': n.message[:100],
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
    } for n in notifs], safe=False)


def admission_form(request):
    programs = Program.objects.all()
    if request.method == 'POST':
        AdmissionApplication.objects.create(
            full_name=request.POST['full_name'],
            father_name=request.POST.get('father_name', ''),
            mother_name=request.POST.get('mother_name', ''),
            dob=request.POST.get('dob') or None,
            gender=request.POST.get('gender', ''),
            applying_program_id=request.POST.get('applying_program_id') or None,
            phone=request.POST['phone'],
            email=request.POST.get('email', ''),
            address=request.POST.get('address', ''),
            previous_institution=request.POST.get('previous_institution', ''),
        )
        messages.success(request, 'Application submitted successfully. We will contact you soon.')
        return redirect('admission_form')
    return render(request, 'admission_form.html', {'programs': programs})


@login_required
def admin_admissions(request):
    if request.user.role != 'admin':
        return redirect('dashboard')
    status = request.GET.get('status', 'pending')
    return render(request, 'admin_admissions.html', {
        'applications': AdmissionApplication.objects.filter(status=status).select_related('applying_program'),
        'current_status': status,
        'statuses': ['pending', 'approved', 'rejected'],
    })
