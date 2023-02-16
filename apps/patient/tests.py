from rest_framework.test import APIClient
from rest_framework import status
from rest_framework import status

from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from apps.authentication.test_helper import BaseHelperTestCase
from apps.hospital.models import Patient

User = get_user_model()


class TestPatientView(BaseHelperTestCase):
    """Test module for inserting a new puppy"""

    def setUp(self):
        self.client = APIClient()

    def test_01_create_valid_patient(self):
        user = self.create_user_for_test(user_type="PATIENT", email="ravi2@gmail.com")
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.create_hospital()
        user = self.get_user()
        hospital = self.get_hospital()
        self.create_screening_name()
        valid_patient_data = {
            "email": "admin12@gmail.com",
            "first_name": "Auto",
            "last_name": "Goyal",
            "profile_pic": None,
            "password": "Myadmin123",
            "user": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "user_type": user.user_type,
            },
            "hospital": hospital.id,
            "title": "345",
            "middle_name": "Singh",
            "dob": "1996-05-24",
            "gender": "MALE",
            "patient_status": "ACTIVE",
        }
        response = self.client.post(
            reverse("patient"), valid_patient_data, format="json"
        )
        middle_name = response.data.get('data')['middle_name']
        response_hospital = response.data.get('data')['hospital']
        self.assertEqual(response_hospital, hospital.id)
        self.assertEqual(middle_name, valid_patient_data.get('middle_name'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.data.get("data")["middle_name"], "Singh")
        self.assertIsNone(response.data.get("errors"))
        print("test_01_create_valid_patient")

    def test_02_create_patient_with_hospital_none(self):
        user = self.create_user_for_test(user_type="PATIENT", email="ravi2@gmail.com")
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.create_hospital()
        user = self.get_user()
        hospital = self.get_hospital()
        self.create_screening_name()
        valid_patient_data = {
            "email": "admin13@gmail.com",
            "first_name": "Anil",
            "last_name": "Soni",
            "profile_pic": None,
            "password": "Myadmin123",
            "user": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "user_type": user.user_type,
            },
            "title": "345",
            "middle_name": "Singh",
            "dob": "1996-05-24",
            "gender": "MALE",
            "patient_status": "ACTIVE",
        }
        response = self.client.post(
            reverse("patient"), valid_patient_data, format="json"
        )
        hospital = response.data.get('data')['hospital']
        gender = response.data.get('data')['gender']
        self.assertEqual(gender, valid_patient_data.get('gender'))
        self.assertEqual(hospital, None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.data.get("data")["middle_name"], "Singh")
        self.assertIsNone(response.data.get("errors"))
        print("test_02_create_patient_with_hospital_none")

    def test_03_create_patient_without_title(self):
        user = self.create_user_for_test(user_type="PATIENT", email="ravi2@gmail.com")
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.create_hospital()
        user = self.get_user()
        hospital = self.get_hospital()
        self.create_screening_name()
        valid_patient_data = {
            "email": "admin13@gmail.com",
            "first_name": "Anil",
            "last_name": "Soni",
            "profile_pic": None,
            "password": "Myadmin123",
            "user": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "user_type": user.user_type,
            },
            "hospital": hospital.id,
            "middle_name": "Singh",
            "dob": "1996-05-24",
            "gender": "MALE",
            "patient_status": "ACTIVE",
        }
        response = self.client.post(
            reverse("patient"), valid_patient_data, format="json"
        )
        title = response.data.get('data')['title']
        self.assertEqual(title, None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.data.get("data")["middle_name"], "Singh")
        self.assertIsNone(response.data.get("errors"))
        print("test_03_create_patient_with_hospital_none")

    def test_04_create_patient_with_middle_name_none(self):
        user = self.create_user_for_test(user_type="PATIENT", email="ravi2@gmail.com")
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.create_hospital()
        user = self.get_user()
        hospital = self.get_hospital()
        self.create_screening_name()
        valid_patient_data = {
            "email": "admin13@gmail.com",
            "first_name": "Anil",
            "last_name": "Soni",
            "profile_pic": None,
            "password": "Myadmin123",
            "user": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "user_type": user.user_type,
            },
            "hospital": hospital.id,
            "title": "345",
            "dob": "1996-05-24",
            "gender": "MALE",
            "patient_status": "ACTIVE",
        }
        response = self.client.post(
            reverse("patient"), valid_patient_data, format="json"
        )
        middle_name = response.data.get('data')['middle_name']
        self.assertEqual(middle_name, valid_patient_data.get('middle_name'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertIsNone(response.data.get("errors"))
        print("test_04_create_patient_with_middle_name_none")

    def test_05_create_patient_with_patient_status_none(self):
        user = self.create_user_for_test(user_type="PATIENT", email="ravi2@gmail.com")
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.create_hospital()
        user = self.get_user()
        hospital = self.get_hospital()
        self.create_screening_name()
        valid_patient_data = {
            "email": "admin13@gmail.com",
            "first_name": "Anil",
            "last_name": "Soni",
            "profile_pic": None,
            "password": "Myadmin123",
            "user": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "user_type": user.user_type,
            },
            "hospital": hospital.id,
            "title": "345",
            "middle_name": "Singh",
            "dob": "1996-05-24",
            "gender": "MALE"
            # "patient_status": "ACTIVE",
        }
        response = self.client.post(
            reverse("patient"), valid_patient_data, format="json"
        )
        patient_status = response.data.get('data')['patient_status']
        self.assertEqual(patient_status, "ACTIVE")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.data.get("data")["middle_name"], "Singh")
        self.assertIsNone(response.data.get("errors"))
        print("test_05_create_patient_with_patient_status_none")

    def test_06_get_all_patient_data(self):
        user = self.create_user_for_test(user_type="PATIENT", email="ravi23@gmail.com")
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.create_screening_name()
        self.create_patient()
        response = self.client.get(reverse("patient"))
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        print("test_06_get_all_patient_data")

    def test_07_get_all_patient_data_length(self):
        user = self.create_user_for_test(user_type="PATIENT", email="ravi23@gmail.com")
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.create_screening_name()
        self.create_patient()
        response = self.client.get(reverse("patient"))
        response_patient_length = len(response.data.get('data'))
        self.assertEqual(response_patient_length, 4)
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        print("test_07_get_all_patient_data_length")


class TestPatientDetailView(BaseHelperTestCase):

    def setUp(self):
        self.client = APIClient()

    def test_01_get_patient_detail_success(self):
        user = self.create_user_for_test(user_type="PATIENT", email="ravi23@gmail.com")
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.create_screening_name()
        self.create_patient()
        patient = Patient.objects.all().first()
        endpoint = f"/api/v1/patient/detail/{patient.id}/"
        response = self.client.get(endpoint)

        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        print("test_01_get_patient_detail_success")

    def test_02_get_patient_detail_with_caremanager_none(self):
        user = self.create_user_for_test(user_type="PATIENT", email="ravi23@gmail.com")
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.create_screening_name()
        self.create_patient()
        patient = Patient.objects.all().first()
        endpoint = f"/api/v1/patient/detail/{patient.id}/"
        response = self.client.get(endpoint)

        response_hospital = response.data.get('data')['hospital']
        self.assertEqual(response_hospital, patient.hospital.id)
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        print("test_02_get_patient_detail_with_caremanager_none")

    def test_03_get_patient_detail_with_caremanager_none(self):
        user = self.create_user_for_test(user_type="PATIENT", email="ravi23@gmail.com")
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.create_screening_name()
        self.create_patient()
        patient = Patient.objects.all().first()
        endpoint = f"/api/v1/patient/detail/{patient.id}/"
        response = self.client.get(endpoint)

        response_caremanager = response.data.get('data')['caremanager']
        self.assertEqual(response_caremanager, patient.caremanager)
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        print("test_03_get_patient_detail_with_caremanager_none")


    def test_04_update_patient_detail_success(self):
        user = self.create_user_for_test(user_type="PATIENT", email="ravi22@gmail.com")
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        hospital = self.get_hospital()
        valid_patient_data = {
            "email": "admin15@gmail.com",
            "first_name": "Anil",
            "last_name": "Jain",
            "profile_pic": None,
            "password": "Myadmin123",
            "user": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "user_type": user.user_type,
            },
            "title": "345",
            "middle_name": "Choudhary",
            "dob": "1996-05-24",
            "gender": "MALE",
            "patient_status": "ACTIVE",
        }
        self.create_screening_name()
        self.create_patient()
        patient = Patient.objects.all().first()
        endpoint = f"/api/v1/patient/detail/{patient.id}/"
        response = self.client.put(endpoint, valid_patient_data, format="json")

        response_middle_name = response.data.get('data')['middle_name']
        self.assertEqual(response_middle_name, valid_patient_data.get('middle_name'))
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        print("test_04_update_patient_detail_success")

    def test_05_delete_patient_detail_success(self):
        user = self.create_user_for_test(user_type="PATIENT", email="ravi22@gmail.com")
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.create_screening_name()
        self.create_patient()
        patient = Patient.objects.all().first()
        endpoint = f"/api/v1/patient/detail/{patient.id}/"
        response = self.client.delete(endpoint)
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        print("test_05_delete_patient_detail_success")
