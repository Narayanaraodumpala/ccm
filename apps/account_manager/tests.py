from rest_framework.test import APIClient
from rest_framework import status

from django.shortcuts import reverse

from apps.authentication.test_helper import BaseHelperTestCase
from apps.hospital.models import Hospital


class TestCareManagerApiView(BaseHelperTestCase):

    def setUp(self):
        self.client = APIClient()
        self.endpoint = '/api/v1/account/manager/caremanager/'
        self.create_hospital()

    def test_01_create_care_manager_message_success(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='ravi2@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        hospital = Hospital.objects.all().last()
        valid_care_manager_data = {
            "email" : "ravi54@gmail.com",
            "password": "Myadmin1234",
            "user_type": "CAREMANAGER",
            "first_name": "Ankit",
            "last_name": "Sharma",
            'hospital': hospital.id,
            'contact': "6260336626",
            'address': "Dindayal Nagar, Ratlam",
            'care_manager_status': "ACTIVE",
            'secondary_email': "farhan@gmail.com",
            'secondary_contact': "6260336626"
        }
        response = self.client.post(
            self.endpoint,
            valid_care_manager_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('message'), 'success')
        self.assertIsNone(response.data.get('errors'))
        print("test_create_care_manager_message_success")

    def test_02_create_care_manager_with_valid_email(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='ravi2@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        hospital = Hospital.objects.all().last()
        valid_care_manager_data = {
            "email" : "ravi54@gmail.com",
            "password": "Myadmin1234",
            "user_type": "CAREMANAGER",
            "first_name": "Ankit",
            "last_name": "Sharma",
            'hospital': hospital.id,
            'contact': "6260336626",
            'address': "Dindayal Nagar, Ratlam",
            'care_manager_status': "ACTIVE",
            'secondary_email': "farhan@gmail.com",
            'secondary_contact': "6260336626"
        }
        response = self.client.post(
            self.endpoint,
            valid_care_manager_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('message'), 'success')
        self.assertNotEqual(response.data.get('message'), 'failed')
        self.assertEqual(response.data.get('data')['email'], 'ravi54@gmail.com')
        self.assertIsNone(response.data.get('errors'))
        print("test_create_care_manager_with_valid_email done")

    def test_03_create_care_manager_with_valid_profile_pic(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='ravi2@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        hospital = Hospital.objects.all().last()
        valid_care_manager_data = {
            "email" : "ravi54@gmail.com",
            "password": "Myadmin1234",
            "user_type": "CAREMANAGER",
            "first_name": "Ankit",
            "last_name": "Sharma",
            'hospital': hospital.id,
            'contact': "6260336626",
            'address': "Dindayal Nagar, Ratlam",
            'care_manager_status': "ACTIVE",
            'secondary_email': "farhan@gmail.com",
            'secondary_contact': "6260336626"
        }
        response = self.client.post(
            self.endpoint,
            valid_care_manager_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('message'), 'success')
        self.assertNotEqual(response.data.get('message'), 'failed')
        self.assertEqual(response.data.get('data')['profile_pic'], None)
        self.assertIsNone(response.data.get('errors'))
        print("test_create_care_manager_with_valid_user_type done")

    def test_04_create_care_manager_with_valid_first_name(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='ravi2@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        hospital = Hospital.objects.all().last()
        valid_care_manager_data = {
            "email" : "ravi54@gmail.com",
            "password": "Myadmin1234",
            "user_type": "CAREMANAGER",
            "first_name": "Ankit",
            "last_name": "Sharma",
            'hospital': hospital.id,
            'contact': "6260336626",
            'address': "Dindayal Nagar, Ratlam",
            'care_manager_status': "ACTIVE",
            'secondary_email': "farhan@gmail.com",
            'secondary_contact': "6260336626"
        }
        response = self.client.post(
            self.endpoint,
            valid_care_manager_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('message'), 'success')
        self.assertNotEqual(response.data.get('message'), 'failed')
        self.assertEqual(response.data.get('data')['first_name'], 'Ankit')
        self.assertIsNone(response.data.get('errors'))
        print("test_create_care_manager_with_valid_first_name done")

    def test_05_create_care_manager_with_valid_last_name(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='ravi2@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        hospital = Hospital.objects.all().last()
        valid_care_manager_data = {
            "email" : "ravi54@gmail.com",
            "password": "Myadmin1234",
            "user_type": "CAREMANAGER",
            "first_name": "Ankit",
            "last_name": "Sharma",
            'hospital': hospital.id,
            'contact': "6260336626",
            'address': "Dindayal Nagar, Ratlam",
            'care_manager_status': "ACTIVE",
            'secondary_email': "farhan@gmail.com",
            'secondary_contact': "6260336626"
        }
        response = self.client.post(
            self.endpoint,
            valid_care_manager_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('message'), 'success')
        self.assertNotEqual(response.data.get('message'), 'failed')
        self.assertEqual(response.data.get('data')['last_name'], 'Sharma')
        self.assertIsNone(response.data.get('errors'))
        print("test_create_care_manager_with_valid_last_name done")

    def test_06_create_care_manager_with_valid_hospital(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='ravi2@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        hospital = Hospital.objects.all().last()
        valid_care_manager_data = {
            "email" : "ravi54@gmail.com",
            "password": "Myadmin1234",
            "user_type": "CAREMANAGER",
            "first_name": "Ankit",
            "last_name": "Sharma",
            'hospital': hospital.id,
            'contact': "6260336626",
            'address': "Dindayal Nagar, Ratlam",
            'care_manager_status': "ACTIVE",
            'secondary_email': "farhan@gmail.com",
            'secondary_contact': "6260336626"
        }
        response = self.client.post(
            self.endpoint,
            valid_care_manager_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('message'), 'success')
        self.assertNotEqual(response.data.get('message'), 'failed')
        self.assertEqual(response.data.get('data')['hospital'], hospital.id)
        self.assertIsNone(response.data.get('errors'))
        print("test_create_care_manager_with_valid_hospital done")

    def test_07_create_care_manager_with_valid_contact(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='ravi2@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        hospital = Hospital.objects.all().last()
        valid_care_manager_data = {
            "email" : "ravi54@gmail.com",
            "password": "Myadmin1234",
            "user_type": "CAREMANAGER",
            "first_name": "Ankit",
            "last_name": "Sharma",
            'hospital': hospital.id,
            'contact': "6260336626",
            'address': "Dindayal Nagar, Ratlam",
            'care_manager_status': "ACTIVE",
            'secondary_email': "farhan@gmail.com",
            'secondary_contact': "6260336626"
        }
        response = self.client.post(
            self.endpoint,
            valid_care_manager_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('message'), 'success')
        self.assertNotEqual(response.data.get('message'), 'failed')
        self.assertEqual(response.data.get('data')['contact'], "6260336626")
        self.assertIsNone(response.data.get('errors'))
        print("test_create_care_manager_with_valid_contact done")

    def test_08_create_care_manager_with_valid_address(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='ravi2@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        hospital = Hospital.objects.all().last()
        valid_care_manager_data = {
            "email" : "ravi54@gmail.com",
            "password": "Myadmin1234",
            "user_type": "CAREMANAGER",
            "first_name": "Ankit",
            "last_name": "Sharma",
            'hospital': hospital.id,
            'contact': "6260336626",
            'address': "Dindayal Nagar, Ratlam",
            'care_manager_status': "ACTIVE",
            'secondary_email': "farhan@gmail.com",
            'secondary_contact': "6260336626"
        }
        response = self.client.post(
            self.endpoint,
            valid_care_manager_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('message'), 'success')
        self.assertNotEqual(response.data.get('message'), 'failed')
        self.assertEqual(response.data.get('data')['address'], "Dindayal Nagar, Ratlam")
        self.assertIsNone(response.data.get('errors'))
        print("test_create_care_manager_with_valid_address done")

    def test_09_create_care_manager_message_failed_with_invalid_email(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='raju12@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        hospital = Hospital.objects.all().last()
        valid_care_manager_data = {
            "email" : user.email,
            "password": "Myadmin1234",
            "user_type": "CAREMANAGER",
            "first_name": "Ankit",
            "last_name": "Sharma",
            'hospital': hospital.id,
            'contact': "6260336626",
            'address': "Dindayal Nagar, Ratlam",
            'care_manager_status': "ACTIVE",
            'secondary_email': "farhan@gmail.com",
            'secondary_contact': "6260336626"
        }
        response = self.client.post(
            self.endpoint,
            valid_care_manager_data,
            format='json'
        )
        response_error = response.data.get('errors')['non_field_errors'][0]

        self.assertNotEqual(response.data.get('message'), 'success')
        self.assertEqual(response_error, "This Email already exist.")
        self.assertIsNone(response.data.get('data'))
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data.get('message'), 'failed')
        print("test_create_care_manager_message_failed_with_invalid_email")

    def test_10_create_care_manager_invalid_contact(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='ravi3@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        hospital = Hospital.objects.all().last()
        valid_care_manager_data = {
            "email" : "ravi54@gmail.com",
            "password": "Myadmin1234",
            "user_type": "CAREMANAGER",
            "first_name": "Ankit",
            "last_name": "Sharma",
            'hospital': hospital.id,
            'contact': None,
            'address': "Dindayal Nagar, Ratlam",
            'care_manager_status': "ACTIVE",
            'secondary_email': "farhan@gmail.com",
            'secondary_contact': "6260336626"
        }
        response = self.client.post(
            self.endpoint,
            valid_care_manager_data,
            format='json'
        )

        self.assertIsNone(response.data.get('data')['contact'])
        self.assertIsNone(response.data.get('errors'))
        self.assertNotEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get('message'), 'failed')
        self.assertEqual(response.data.get('message'), 'success')
        print("test_create_care_manager_invalid_contact")

    def test_11_create_care_manager_invalid_address(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='ravi4@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        hospital = Hospital.objects.all().last()
        valid_care_manager_data = {
            "email" : "ravi54@gmail.com",
            "password": "Myadmin1234",
            "user_type": "CAREMANAGER",
            "first_name": "Ankit",
            "last_name": "Sharma",
            'hospital': hospital.id,
            'contact': "9074606891",
            'address': None,
            'care_manager_status': "ACTIVE",
            'secondary_email': "farhan@gmail.com",
            'secondary_contact': "6260336626"
        }
        response = self.client.post(
            self.endpoint,
            valid_care_manager_data,
            format='json'
        )

        self.assertIsNotNone(response.data.get('errors'))
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get('message'), 'success')
        self.assertEqual(response.data.get('message'), 'failed')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("test_create_care_manager_invalid_address")

    def test_12_get_care_manager_list_message_success(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='ravi5@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.create_care_manager()
        response = self.client.get(self.endpoint)

        self.assertIsNone(response.data.get('errors'))
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get('message'), 'failed')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('message'), 'success')
        print("test_get_care_manager_list_message_success")

    def test_13_get_care_manager_list_errors_none(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='shark@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.create_care_manager()
        response = self.client.get(self.endpoint)

        self.assertIsNone(response.data.get('errors'))
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get('message'), 'failed')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('errors'), None)
        print("test_get_care_manager_list_errors_none")

    def test_14_get_care_manager_list_valid_user(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='shark12@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.create_care_manager()
        response = self.client.get(self.endpoint)
        user_email = response.data.get('data')[0]['email']

        self.assertIsNone(response.data.get('errors'))
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get('message'), 'failed')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("test_get_care_manager_list_valid_user")

    def test_15_get_care_manager_list_valid_hospital(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='shrak13@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.create_care_manager()
        hospital = Hospital.objects.all().last()
        response = self.client.get(self.endpoint)
        caremanager_hospital = response.data.get('data')[0]['hospital']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(caremanager_hospital, hospital.id)
        self.assertIsNone(response.data.get('errors'))
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get('message'), 'failed')
        print("test_get_care_manager_list_valid_hospital")

    def test_16_get_care_manager_list_valid_profile_pic(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='shark14@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.create_care_manager()
        response = self.client.get(self.endpoint)
        profile_pic = response.data.get('data')[0]['profile_pic']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_pic, None)
        self.assertIsNone(response.data.get('errors'))
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get('message'), 'failed')
        print("test_get_care_manager_list_valid_profile_pic")

    def test_17_get_care_manager_list_valid_hospital_branch(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='shrak15@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.create_care_manager()
        response = self.client.get(self.endpoint)
        hospital_branch = response.data.get('data')[0]['hospital_branch']

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(hospital_branch, [])
        self.assertIsNone(response.data.get('errors'))
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get('message'), 'failed')
        print("test_get_care_manager_list_valid_hospital_branch")


class TestManagerRetriveApiView(BaseHelperTestCase):
    """ Test module for user login """

    def setUp(self):
        self.client = APIClient()
        self.hospital = self.create_hospital()

    def test_01_get_care_manager_message_success(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='ravi12@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.create_care_manager()
        caremanager = self.get_caremanager()
        endpoint = f'/api/v1/account/manager/caremanager/retrive/{caremanager.id}/'
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('message'), 'success')
        self.assertIsNone(response.data.get('errors'))
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get('message'), 'failed')
        print("test_get_care_manager_message_success")

    def test_02_get_care_manager_errors_none(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='ravi13@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.create_care_manager()
        caremanager = self.get_caremanager()
        endpoint = f'/api/v1/account/manager/caremanager/retrive/{caremanager.id}/'
        response = self.client.get(endpoint)
        self.assertIsNone(response.data.get('errors'))
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get('message'), 'failed')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('errors'), None)
        print("test_get_care_manager_errors_none")

    def test_03_get_care_manager_valid_user(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='raju13@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.create_care_manager()
        caremanager = self.get_caremanager()
        endpoint = f'/api/v1/account/manager/caremanager/retrive/{caremanager.id}/'
        response = self.client.get(endpoint)
        user_email = response.data.get('data')['email']

        self.assertIsNone(response.data.get('errors'))
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get('message'), 'failed')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user_email, caremanager.user.email)
        print("test_get_care_manager_valid_user")

    def test_04_get_care_manager_valid_hospital(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='raju14@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.create_care_manager()
        caremanager = self.get_caremanager()
        endpoint = f'/api/v1/account/manager/caremanager/retrive/{caremanager.id}/'
        response = self.client.get(endpoint)
        hospital = response.data.get('data')['hospital']
        self.assertIsNone(response.data.get('errors'))
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get('message'), 'failed')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(hospital, caremanager.hospital.id)
        print("test_get_care_manager_valid_hospital")

    def test_05_get_care_manager_valid_secondary_email(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='raju15@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.create_care_manager()
        caremanager = self.get_caremanager()
        endpoint = f'/api/v1/account/manager/caremanager/retrive/{caremanager.id}/'
        response = self.client.get(endpoint)
        secondary_email = response.data.get('data')['secondary_email']

        self.assertIsNone(response.data.get('errors'))
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get('message'), 'failed')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(secondary_email, caremanager.secondary_email)
        print("test_get_care_manager_valid_secondary_email")

    def test_06_get_care_manager_invalid_with_id(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='raju16@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.create_care_manager()
        caremanager = self.get_caremanager()
        endpoint = f'/api/v1/account/manager/caremanager/retrive/{caremanager.id}0/'
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('message'), 'failed')
        self.assertIsNotNone(response.data.get('errors'))
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get('message'), 'success')
        print("test_get_care_manager_invalid_with_id")

    def test_07_get_care_manager_invalid_with_data(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='raju17@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.create_care_manager()
        caremanager = self.get_caremanager()
        endpoint = f'/api/v1/account/manager/caremanager/retrive/{caremanager.id}0/'
        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('data'), None)
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get('message'), 'success')
        print("test_get_care_manager_invalid_with_data")

    def test_08_get_care_manager_invalid_with_errors(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='raju18@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.create_care_manager()
        caremanager = self.get_caremanager()
        endpoint = f'/api/v1/account/manager/caremanager/retrive/{caremanager.id}0/'
        response = self.client.get(endpoint)
        response_error = response.data.get('errors')['non_field_errors']
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_error, ['failed'])
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get('message'), 'success')
        print("test_get_care_manager_invalid_with_errors")

    def test_09_update_care_manager_valid_secondary_email(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='raju19@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.create_care_manager()
        caremanager = self.get_caremanager()
        endpoint = f'/api/v1/account/manager/caremanager/retrive/{caremanager.id}/'
        updated_caremanager = {
            "email": "hansran@gmail.com",
            "first_name": "Hans",
            "last_name": "Raj",
            "secondary_email": "seocnnd@gmail.com",
            "address": "Dindayal Nagar Ratlam"
        }
        response = self.client.put(
            endpoint,
            updated_caremanager,
            format='json'
        )
        self.assertIsNone(response.data.get('errors'))
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get('message'), 'failed')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('message'), 'success')
        print("test_update_care_manager_valid_secondary_email")

    def test_10_update_care_manager_invalid_with_null_address(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='raju20@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.create_care_manager()
        caremanager = self.get_caremanager()
        endpoint = f'/api/v1/account/manager/caremanager/retrive/{caremanager.id}/'
        updated_caremanager = {
            "email": "hansran@gmail.com",
            "first_name": "Hans",
            "last_name": "Raj",
            "secondary_email": "seocnnd@gmail.com"
        }
        response = self.client.put(
            endpoint,
            updated_caremanager,
            format='json'
        )
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get('message'), 'success')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('message'), 'failed')
        print("test_update_care_manager_invalid_with_null_address")

    def test_11_update_care_manager_invalid_with_null_secondary_email(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='raju121@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.create_care_manager()
        caremanager = self.get_caremanager()
        endpoint = f'/api/v1/account/manager/caremanager/retrive/{caremanager.id}/'
        updated_caremanager = {
            "email": "hansran@gmail.com",
            "first_name": "Hans",
            "last_name": "Raj",
            "address": "Dindayal Nagar Ratlam"
        }
        response = self.client.put(
            endpoint,
            updated_caremanager,
            format='json'
        )
        self.assertIsNone(response.data.get('errors'))
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get('message'), 'failed')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('message'), 'success')
        print("test_update_care_manager_invalid_with_null_secondary_email")


    def test_12_delete_care_manager_object_message_success(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='raju122@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.create_care_manager()
        caremanager = self.get_caremanager()
        endpoint = f'/api/v1/account/manager/caremanager/retrive/{caremanager.id}/'
        response = self.client.delete(endpoint)
        self.assertIsNone(response.data.get('errors'))
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get('message'), 'failed')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('message'), 'success')
        print("test_delete_care_manager_object_message_success")

    def test_13_delete_care_manager_object_message_failed(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='raju124@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.create_care_manager()
        caremanager = self.get_caremanager()
        endpoint = f'/api/v1/account/manager/caremanager/retrive/{caremanager.id}0/'
        response = self.client.delete(endpoint)
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get('message'), 'success')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data.get('message'), 'failed')
        print("test_delete_care_manager_object_message_failed")

    def test_14_delete_care_manager_check_is_active(self):
        user = self.create_user_for_test(user_type='SUPERADMIN', email='raju155@gmail.com')
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.create_care_manager()
        caremanager = self.get_caremanager()
        endpoint = f'/api/v1/account/manager/caremanager/retrive/{caremanager.id}/'
        response = self.client.delete(endpoint)
        updated_caremanager = self.get_caremanager()
        self.assertIsNone(response.data.get('errors'))
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get('message'), 'failed')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_caremanager.is_active, False)
        self.assertEqual(response.data.get('data'), None)
        print("test_delete_care_manager_check_is_active")
