# attendance/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import time

class Organization(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    allowed_radius_meters = models.FloatField(default=100.0)  # e.g., 100 meters
    start_time = models.TimeField(default=time(7, 0))   # 7:00 AM
    end_time = models.TimeField(default=time(16, 0))    # 5:00 PM

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    staff_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.full_name} ({self.staff_id})"


class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,null=True,blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    sign_in_time = models.DateTimeField(default=timezone.now)
    sign_out_time = models.DateTimeField(null=True, blank=True)
    is_late = models.BooleanField(default=False)
    early_sign_in = models.BooleanField(default=False)
    early_sign_out = models.BooleanField(default=False)
    is_absent = models.BooleanField(default=False)
    total_hours = models.FloatField(default=0.0)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.employee.full_name if self.employee else 'Unknown Employee'} - {self.date}"

    def mark_lateness(self):
        if self.sign_in_time and self.organization.start_time:
            start_dt = timezone.make_aware(
                timezone.datetime.combine(self.date, self.organization.start_time)
            )
            if self.sign_in_time > start_dt:
                self.is_late = True
                self.remarks = f"Late by {(self.sign_in_time - start_dt).seconds // 60} minutes"
        self.save()

    def compute_total_hours(self):
        if self.sign_in_time and self.sign_out_time:
            delta = self.sign_out_time - self.sign_in_time
            self.total_hours = round(delta.total_seconds() / 3600, 2)
        self.save()
