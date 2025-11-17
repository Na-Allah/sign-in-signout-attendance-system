# attendance/management/commands/mark_absents.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from attendance.models import Attendance, Employee, Organization

class Command(BaseCommand):
    help = "Mark absent employees who did not sign in today"

    def handle(self, *args, **kwargs):
        today = timezone.localtime().date()
        org = Organization.objects.first()
        employees = Employee.objects.all()

        for emp in employees:
            if Attendance.objects.filter(employee=emp, date=today).exists():
                continue
            Attendance.objects.create(
                employee=emp,
                organization=org,
                date=today,
                is_absent=True,
                remarks="Did not sign in"
            )
            self.stdout.write(self.style.SUCCESS(f"Marked absent: {emp.full_name}"))
