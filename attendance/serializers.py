# attendance/serializers.py
from rest_framework import serializers
from .models import AttendanceRecord

class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'user', 'organization', 'shift', 'date',
            'sign_in_time','sign_out_time',
            'sign_in_lat','sign_in_lon','sign_out_lat','sign_out_lon',
            'status','notes'
        ]
        read_only_fields = ['id', 'status', 'sign_in_time', 'sign_out_time']
