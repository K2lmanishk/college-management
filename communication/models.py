from django.db import models
from accounts.models import User


class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    audience = models.CharField(max_length=20, default='all')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Notification(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, default='general')
    audience = models.CharField(max_length=20, default='all')
    specific_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='personal_notifications')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    expiry_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class AdmissionApplication(models.Model):
    full_name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100, blank=True)
    mother_name = models.CharField(max_length=100, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    applying_program = models.ForeignKey('accounts.Program', on_delete=models.SET_NULL, null=True)
    semester = models.CharField(max_length=50, default='Semester 1')
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    previous_institution = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, default='pending')
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.status})"
