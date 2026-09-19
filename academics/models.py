from django.db import models
from accounts.models import Program, Student, Faculty


class Subject(models.Model):
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True, blank=True, related_name='subjects')
    semester = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    credits = models.PositiveIntegerField(default=3)
    type = models.CharField(max_length=20, default='Theory')

    def __str__(self):
        return f"{self.name} ({self.code})"


class FacultyAssignment(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='assignments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=20, default='2025-2026')

    def __str__(self):
        return f"{self.faculty} -> {self.subject}"


class Timetable(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True, blank=True)
    semester = models.CharField(max_length=50)
    day = models.CharField(max_length=20)
    time_slot = models.CharField(max_length=50)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    room_no = models.CharField(max_length=20, blank=True)


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, default='Absent')


class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam_type = models.CharField(max_length=50)
    max_marks = models.IntegerField(default=100)
    obtained_marks = models.FloatField()


class Exam(models.Model):
    name = models.CharField(max_length=100)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    semester = models.CharField(max_length=50)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam_date = models.DateField()
    max_marks = models.IntegerField(default=100)
    passing_marks = models.IntegerField(default=40)
    academic_year = models.CharField(max_length=20, default='2025-2026')


class ExamResult(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    obtained_marks = models.FloatField()
    grade = models.CharField(max_length=5, blank=True)
    remarks = models.CharField(max_length=200, blank=True)
