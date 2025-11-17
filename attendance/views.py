from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, time
from django.conf import settings
from django.shortcuts import redirect

import attendance
from .models import Attendance, Employee, Organization
from .utils import is_within_radius  # assuming you placed haversine helper here
from geopy.distance import geodesic



import logging

logger = logging.getLogger(__name__)
@login_required
def signin_view(request):
    user = request.user
    try:
        employee = Employee.objects.get(user=user)
    except Employee.DoesNotExist:
        messages.error(request, "Employee profile not found.")
        return redirect("login")

    org = Organization.objects.first()  # adjust if multiple orgs
    now = timezone.localtime()
    today = now.date()

    if request.method == "POST":
        # 🔒 Prevent multiple sign-ins on POST only
        existing_attendance = Attendance.objects.filter(employee=employee, date=today).first()
        if existing_attendance and existing_attendance.sign_in_time:
            messages.error(request, "You have already signed in today.")
            return redirect("signin")

        try:
            lat = float(request.POST.get("latitude", 0))
            lon = float(request.POST.get("longitude", 0))
        except (TypeError, ValueError):
            messages.error(request, "Invalid location data.")
            return redirect("signin")

        user_loc = (lat, lon)
        org_loc = (org.latitude, org.longitude)
        distance = geodesic(user_loc, org_loc).meters
        logger.info(f"User {user.username} is {distance:.1f}m from org location.")

        if distance > org.allowed_radius_meters:
            messages.error(
                request,
                f"You are {distance:.1f} meters away from the allowed sign-in area. "
                f"Allowed radius is {org.allowed_radius_meters} m."
            )
            return redirect("signin")

        attendance, created = Attendance.objects.get_or_create(
            employee=employee, date=today, organization=org
        )

        start_dt = timezone.make_aware(
            timezone.datetime.combine(today, org.start_time)
        )
        late_threshold = start_dt + timezone.timedelta(hours=1)

        attendance.sign_in_time = now
        if now < start_dt:
            attendance.early_sign_in = True
            messages.info(request, "You signed in early.")
        elif now > late_threshold:
            attendance.is_late = True
            messages.warning(request, "You are late.")
        else:
            messages.success(request, "Sign-in recorded successfully.")

        attendance.save()
        return redirect("signin")

    # GET request — just render template
    attendance = Attendance.objects.filter(employee=employee, date=today).first()
    return render(request, "attendance/signin.html", {"attendance": attendance})


@login_required
def signout_view(request):
    user = request.user
    try:
        employee = Employee.objects.get(user=user)
    except Employee.DoesNotExist:
        messages.error(request, "Employee profile not found.")
        return redirect("login")

    org = Organization.objects.first()
    now = timezone.localtime()
    today = now.date()

    try:
        attendance = Attendance.objects.get(employee=employee, date=today)
    except Attendance.DoesNotExist:
        messages.error(request, "You haven’t signed in today.")
        return redirect("signin")

    if request.method == "POST":
        lat = float(request.POST.get("latitude", 0))
        lon = float(request.POST.get("longitude", 0))
        user_loc = (lat, lon)
        org_loc = (org.latitude, org.longitude)
        distance = geodesic(user_loc, org_loc).meters

        if distance > org.allowed_radius_meters:
            messages.error(request, "You are not within the allowed sign-out area.")
            return redirect("signin")

        # 🔒 Prevent early sign-out before end_time
        end_dt = timezone.make_aware(
            timezone.datetime.combine(today, org.end_time)
        )
        if now < end_dt:
            messages.error(
                request,
                f"You cannot sign out before the scheduled end time: {org.end_time.strftime('%H:%M')}."
            )
            return redirect("signin")

        # Sign-out allowed
        attendance.sign_out_time = now
        attendance.compute_total_hours()
        attendance.save()
        messages.success(request, f"Sign-out recorded. Total hours: {attendance.total_hours}")
        return redirect("login")

    return redirect("signin")


    
def login_view(request):
    """
    Handle user login and render the login page.
    """
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('signin')  # redirect to sign-in page after login
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'attendance/login.html')


@login_required(login_url='login')
def logout_view(request):
    """
    Log out the user and redirect to the login page.
    """
    logout(request)
    messages.info(request, "You’ve been logged out successfully.")
    return redirect('login')

@staff_member_required
def attendance_history(request):
    """Admin view to see all attendance records."""
    attendance = Attendance.objects.all()
    return render(request, "attendance/history.html", {"attendance": attendance})