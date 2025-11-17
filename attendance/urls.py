# attendance/urls.py
from django.urls import path
from .views import attendance_history, signin_view, login_view, logout_view, signout_view


urlpatterns = [
  path('',signin_view ,name='signin' ),
  path('signout/', signout_view, name='signout'),
  path('login/', login_view, name='login'),
  path('logout/', logout_view, name='logout'),
  path("history/", attendance_history, name="attendance_history"),
]
