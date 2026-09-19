from django.contrib import admin
from .models import Notice, Notification, AdmissionApplication

admin.site.register(Notice)
admin.site.register(Notification)
admin.site.register(AdmissionApplication)
