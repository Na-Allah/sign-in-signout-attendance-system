# attendance/tests.py
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from .models import Organization, Shift, AttendanceRecord
import datetime
from .utils import haversine_distance_m

User = get_user_model()

class AttendanceAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='alice', email='a@example.com', password='pass')
        self.org = Organization.objects.create(name='HQ', center_lat=6.524379, center_lon=3.379206, geofence_radius_m=200)
        self.shift = Shift.objects.create(
            organization=self.org,
            name='day',
            start_time=datetime.time(9,0),
            end_time=datetime.time(17,0),
            sign_in_open_before=datetime.timedelta(minutes=15),
            sign_in_close_after=datetime.timedelta(minutes=10),
            late_threshold=datetime.timedelta(minutes=5),
            sign_out_open_before=datetime.timedelta(minutes=0),
            sign_out_close_after=datetime.timedelta(hours=2),
        )
        self.url = reverse('record-attendance')

    def test_haversine_zero(self):
        d = haversine_distance_m(6.524379,3.379206,6.524379,3.379206)
        self.assertAlmostEqual(d, 0, delta=0.1)

    def test_sign_in_success(self):
        self.client.login(username='alice', password='pass')
        # fake a location inside geofence (same as center)
        resp = self.client.post(self.url, data={
            'action': 'sign_in',
            'lat': float(self.org.center_lat),
            'lon': float(self.org.center_lon),
            'organization_id': self.org.id
        }, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('ok'))
        # record exists
        ar = AttendanceRecord.objects.filter(user=self.user, organization=self.org, date=timezone.localdate()).first()
        self.assertIsNotNone(ar)
        self.assertIsNotNone(ar.sign_in_time)

    def test_sign_in_out_of_geofence(self):
        self.client.login(username='alice', password='pass')
        resp = self.client.post(self.url, data={
            'action': 'sign_in',
            'lat': 0.0,  # far away
            'lon': 0.0,
            'organization_id': self.org.id
        }, content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertEqual(data.get('error'), 'out_of_geofence')

    def test_sign_out_without_signin(self):
        self.client.login(username='alice', password='pass')
        resp = self.client.post(self.url, data={
            'action': 'sign_out',
            'lat': float(self.org.center_lat),
            'lon': float(self.org.center_lon),
            'organization_id': self.org.id
        }, content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json().get('error'), 'no_signin_record')
