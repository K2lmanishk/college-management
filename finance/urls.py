from django.urls import path
from . import views

urlpatterns = [
    path('admin-panel/fees/', views.admin_manage_fees, name='admin_manage_fees'),
    path('admin-panel/fees/record-payment/', views.record_payment, name='record_payment'),
    path('admin-panel/program-semester-fees/', views.manage_program_semester_fees, name='manage_program_semester_fees'),
    path('api/fee-summary/', views.fee_summary_api, name='fee_summary_api'),
    path('student/fees/', views.view_fees, name='view_fees'),
]
