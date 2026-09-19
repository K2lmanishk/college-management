from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('faculty', 'Faculty'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    full_name = models.CharField(max_length=100, blank=True)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Superusers created via `createsuperuser` automatically become admins
        if self.is_superuser and self.role == 'student':
            self.role = 'admin'
        if self.is_superuser and not self.full_name:
            self.full_name = self.username
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Program(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    duration_years = models.PositiveIntegerField(default=3)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    roll_no = models.CharField(max_length=20, unique=True)
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    semester = models.CharField(max_length=50, blank=True)
    dob = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    parent_contact = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.roll_no} - {self.user.full_name}"


class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    department = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    joining_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.full_name or self.user.username
