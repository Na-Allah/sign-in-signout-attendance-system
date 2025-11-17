# attendance/admin.py
from django.contrib import admin
from .models import Organization, Employee, Attendance

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "latitude", "longitude", "allowed_radius_meters", "start_time", "end_time")

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("staff_id", "full_name", "email", "user")

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "date", "sign_in_time", "sign_out_time", "is_late", "early_sign_in", "early_sign_out", "is_absent", "total_hours")
    list_filter = ("date", "is_late", "early_sign_in", "early_sign_out", "is_absent")
