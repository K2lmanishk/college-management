from django.urls import path
from . import views

urlpatterns = [
    path('admin-panel/notices/', views.manage_notices, name='manage_notices'),
    path('admin-panel/notices/delete/<int:notice_id>/', views.delete_notice, name='delete_notice'),
    path('api/notifications/unread/', views.unread_notifications_api, name='unread_notifications'),
    path('admission/', views.admission_form, name='admission_form'),
    path('admin-panel/admissions/', views.admin_admissions, name='admin_admissions'),
]
