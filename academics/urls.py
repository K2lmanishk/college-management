from django.urls import path
from . import views

urlpatterns = [
    path('admin-panel/subjects/', views.manage_subjects, name='manage_subjects'),
    path('faculty/attendance/', views.mark_attendance, name='mark_attendance'),
    path('faculty/marks/', views.enter_marks, name='enter_marks'),
    path('api/students-by-subject/<int:subject_id>/', views.get_students_by_subject, name='get_students_by_subject'),
    path('student/attendance/', views.student_attendance, name='student_attendance'),
    path('student/marks/', views.student_marks, name='student_marks'),
]
