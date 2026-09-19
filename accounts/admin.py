from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Student, Faculty, Program


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'full_name', 'is_active')
    list_filter = ('role', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('College', {'fields': ('role', 'full_name', 'profile_pic')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('College', {'fields': ('role', 'full_name')}),
    )


admin.site.register(Student)
admin.site.register(Faculty)
admin.site.register(Program)
