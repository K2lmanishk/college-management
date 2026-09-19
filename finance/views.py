from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Fee, ProgramSemesterFee
from accounts.models import Program

SEMESTERS = [f'Semester {i}' for i in range(1, 9)]


@login_required
def admin_manage_fees(request):
    if request.user.role != 'admin':
        return redirect('dashboard')
    fees = Fee.objects.select_related('student__user', 'student__program')
    total_fees = fees.aggregate(s=Sum('amount'))['s'] or 0
    total_paid = fees.aggregate(s=Sum('paid_amount'))['s'] or 0
    pending = fees.exclude(status='Paid').count()
    return render(request, 'admin_fees.html', {
        'fees': fees, 'total_fees': total_fees, 'total_paid': total_paid,
        'total_due': total_fees - total_paid, 'pending_count': pending,
    })


@login_required
@require_POST
def record_payment(request):
    if request.user.role != 'admin':
        return redirect('dashboard')
    fee = get_object_or_404(Fee, id=request.POST['fee_id'])
    try:
        amt = float(request.POST.get('payment_amount', 0))
    except ValueError:
        amt = 0
    if amt <= 0:
        messages.error(request, 'Invalid amount')
        return redirect('admin_manage_fees')
    fee.paid_amount += amt
    fee.status = 'Paid' if fee.paid_amount >= fee.amount else 'Partial'
    fee.payment_method = request.POST.get('payment_method', 'Cash')
    fee.transaction_id = request.POST.get('transaction_id', '')
    fee.remarks = request.POST.get('remarks', '')
    fee.payment_date = timezone.now()
    fee.save()
    messages.success(request, 'Payment recorded')
    return redirect('admin_manage_fees')


@login_required
def fee_summary_api(request):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    total = Fee.objects.aggregate(s=Sum('amount'))['s'] or 0
    collected = Fee.objects.aggregate(s=Sum('paid_amount'))['s'] or 0
    return JsonResponse({'total_fees': float(total), 'total_collected': float(collected)})


@login_required
def manage_program_semester_fees(request):
    if request.user.role != 'admin':
        return redirect('dashboard')
    if request.method == 'POST':
        ProgramSemesterFee.objects.update_or_create(
            program_id=request.POST['program_id'],
            semester=request.POST['semester'],
            defaults={'fee_amount': float(request.POST['fee_amount'])},
        )
        messages.success(request, 'Fee structure saved')
        return redirect('manage_program_semester_fees')
    return render(request, 'manage_program_semester_fees.html', {
        'fees': ProgramSemesterFee.objects.select_related('program'),
        'programs': Program.objects.all(),
        'semesters': SEMESTERS,
    })


@login_required
def view_fees(request):
    if request.user.role != 'student':
        return redirect('dashboard')
    student = getattr(request.user, 'student_profile', None)
    fees = Fee.objects.filter(student=student) if student else []
    return render(request, 'student_fees.html', {'fees': fees})
