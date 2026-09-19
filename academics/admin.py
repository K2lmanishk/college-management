from django.contrib import admin
from .models import Subject, FacultyAssignment, Timetable, Attendance, Marks, Exam, ExamResult

admin.site.register([Subject, FacultyAssignment, Timetable, Attendance, Marks, Exam, ExamResult])
