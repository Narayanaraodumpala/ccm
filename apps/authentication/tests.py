from rest_framework.test import APIClient
from rest_framework import status
from rest_framework import status

from django.shortcuts import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode

from apps.authentication.test_helper import BaseHelperTestCase
from apps.authentication.models import MyProfile

User = get_user_model()


class TestUserLoginView(BaseHelperTestCase):
    """Test module for user login"""

    def setUp(self):
        self.client = APIClient()

    def test_01_valid_login_with_user_type_admin(self):
        user2 = self.create_user_for_test(
            user_type="SUPERADMIN", email="ravi@gmail.com"
        )
        valid_login_data = {"email": "ravi@gmail.com", "password": "Myadmin123"}
        response = self.client.post(
            reverse("user-login"), valid_login_data, format="json"
        )
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertIsNone(response.data.get("errors"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        print("test_valid_login_with_user_type_admin done")

    def test_02_valid_login_with_user_type_practice_admin(self):
        user2 = self.create_user_for_test(
            user_type="PRACTICEADMIN", email="jagdish@gmail.com"
        )
        valid_login_data = {"email": "jagdish@gmail.com", "password": "Myadmin123"}
        response = self.client.post(
            reverse("user-login"), valid_login_data, format="json"
        )
        user_type = response.data.get("data")["user_type"]

        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertIsNone(response.data.get("errors"))
        self.assertEqual(user_type, "PRACTICEADMIN")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        print("test_valid_login_with_user_type_practice_admin")

    def test_03_valid_login_with_user_type_provider(self):
        user3 = self.create_user_for_test(
            user_type="PROVIDER", email="raju12@gmail.com"
        )
        valid_login_data = {"email": "raju12@gmail.com", "password": "Myadmin123"}
        response = self.client.post(
            reverse("user-login"), valid_login_data, format="json"
        )
        user_type = response.data.get("data")["user_type"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        self.assertEqual(user_type, "PROVIDER")
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertIsNone(response.data.get("errors"))
        print("test_valid_login_with_user_type_provider")

    def test_04_valid_login_with_user_type_care_manager(self):
        user3 = self.create_user_for_test(
            user_type="CAREMANAGER", email="raju13@gmail.com"
        )
        valid_login_data = {"email": "raju13@gmail.com", "password": "Myadmin123"}
        response = self.client.post(
            reverse("user-login"), valid_login_data, format="json"
        )
        user_type = response.data.get("data")["user_type"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        self.assertEqual(user_type, "CAREMANAGER")
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertIsNone(response.data.get("errors"))
        print("test_valid_login_with_user_type_care_manager")

    def test_05_valid_login_with_user_type_patient(self):
        user3 = self.create_user_for_test(user_type="PATIENT", email="raju14@gmail.com")
        valid_login_data = {"email": "raju14@gmail.com", "password": "Myadmin123"}
        response = self.client.post(
            reverse("user-login"), valid_login_data, format="json"
        )
        user_type = response.data.get("data")["user_type"]

        self.assertEqual(user_type, "PATIENT")
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertIsNone(response.data.get("errors"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        print("test_valid_login_with_user_type_patient")

    def test_06_valid_login_with_invalid_login_with_no_password(self):
        user2 = self.create_user_for_test(
            user_type="CAREMANAGER", email="sushan@gmail.com"
        )
        valid_login_data = {
            "email": "sushan@gmail.com"
            # "password": "Myadmin123"
        }
        response = self.client.post(
            reverse("user-login"), valid_login_data, format="json"
        )
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get("message"), "success")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("data"), None)
        self.assertEqual(response.data.get("message"), "failed")
        print("test_valid_login_with_invalid_login_with_no_password done")

    def test_07_valid_login_with_errors_none(self):
        user2 = self.create_user_for_test(
            user_type="CAREMANAGER", email="waris@gmail.com"
        )
        valid_login_data = {"email": "waris@gmail.com", "password": "Myadmin123"}
        response = self.client.post(
            reverse("user-login"), valid_login_data, format="json"
        )
        self.assertEqual(user2.user_type, "CAREMANAGER")
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertIsNone(response.data.get("errors"))
        self.assertEqual(response.data.get("message"), "success")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("errors"), None)
        print("test_valid_login_with_errors_none")

    def test_08_invalid_login_with_invalid_password(self):
        user2 = self.create_user_for_test(
            user_type="CAREMANAGER", email="sonu@gmail.com"
        )
        valid_login_data = {"email": "sonu@gmail.com", "password": "Myadmin1234455"}
        response = self.client.post(
            reverse("user-login"), valid_login_data, format="json"
        )
        response_error = response.data.get("errors")["non_field_errors"][0]

        self.assertEqual(user2.user_type, "CAREMANAGER")
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get("message"), "success")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("message"), "failed")
        self.assertEqual(response_error.code, "invalid")
        print("test_invalid_login_with_invalid_password")


class TestRequestPasswordResetEmailView(BaseHelperTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_01_password_reset_success(self):
        user = self.create_user_for_test(
            user_type="CAREMANAGER", email="mogen90493@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        response = self.client.post(
            reverse("request-reset-email"), {"email": user.email}, format="json"
        )
        self.assertEqual(user.user_type, "CAREMANAGER")
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        print("test_password_reset_success")

    def test_02_password_reset_message_failed(self):
        user = self.create_user_for_test(
            user_type="CAREMANAGER", email="mogen9049333@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        user2_email = "mogen905558@octovie.com"
        response = self.client.post(
            reverse("request-reset-email"), {"email": user2_email}, format="json"
        )

        self.assertEqual(user.user_type, "CAREMANAGER")
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get("message"), "success")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("message"), "failed")
        print("test_password_reset_message_failed")

    def test_03_password_reset_errors_user_not_found(self):
        user = self.create_user_for_test(
            user_type="CAREMANAGER", email="mogen9049333@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        user2_email = "mogen905558@octovie.com"
        response = self.client.post(
            reverse("request-reset-email"), {"email": user2_email}, format="json"
        )
        response_error = response.data.get("errors")["non_field_errors"]
        self.assertEqual(response_error, ["User not found"])
        self.assertEqual(user.user_type, "CAREMANAGER")
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get("message"), "success")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("test_password_reset_errors_user_not_found done")


class TestPasswordTokenCheckAPIView(BaseHelperTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_01_password_token_check_message_failed(self):
        user = self.create_user_for_test(
            user_type="CAREMANAGER", email="mogen904@gmail.com"
        )
        token = self.user_login(email=user.email)
        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        response = self.client.get(
            reverse("confirm-password", kwargs={"uidb64": uidb64, "token": token})
        )
        self.assertEqual(user.user_type, "CAREMANAGER")
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data.get("message"), "token is not valid, please check the new one"
        )
        print("test_password_token_check_message_failed")


class TestSetNewPasswordAPIView(BaseHelperTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_01_set_new_password_message_failed(self):
        user = self.create_user_for_test(
            user_type="CAREMANAGER", email="mogen901@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        reset_password = {
            "new_password": "Myadmin123",
            "confirm_password": "Myadmin123",
            "token": token,
            "uidb64": urlsafe_base64_encode(smart_bytes(user.id)),
        }
        response = self.client.patch(
            reverse("password-reset-complete"), reset_password, format="json"
        )

        self.assertEqual(user.user_type, "CAREMANAGER")
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "success")
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data.get("message"), "failed")
        print("test_set_new_password_message_failed")

    def test_02_set_new_password_message_invalid_confirm_password(self):
        user = self.create_user_for_test(
            user_type="CAREMANAGER", email="mongo5444db@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        reset_password = {
            "new_password": "Myadmin123",
            "confirm_password": "Myadmin12345",
            "token": token,
            "uidb64": urlsafe_base64_encode(smart_bytes(user.id)),
        }
        response = self.client.patch(
            reverse("password-reset-complete"), reset_password, format="json"
        )
        self.assertEqual(user.user_type, "CAREMANAGER")
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "success")
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "failed")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIsNone(response.data.get("data"))
        print("test_set_new_password_message_invalid_confirm_password done")


class TestMyProfileView(BaseHelperTestCase):
    def setUp(self):
        self.client = APIClient()
        self.endpoint = "/api/v1/authentication/my_profile/"

    def test_01_get_myprofile_all_data_with_message_success(self):
        user = self.create_user_for_test(
            user_type="CAREMANAGER", email="mogen90@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.create_myprofile()
        response = self.client.get(self.endpoint)
        self.assertEqual(user.user_type, "CAREMANAGER")
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        print("test_get_myprofile_all_data_with_message_success done")

    def test_02_get_myprofile_all_data_with_total_objects(self):
        user = self.create_user_for_test(
            user_type="CAREMANAGER", email="mogen90@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.create_myprofile()
        response = self.client.get(self.endpoint)

        my_profiles_in_response = response.data.get("data")
        myprofiles = MyProfile.objects.all()

        self.assertEqual(len(myprofiles), len(my_profiles_in_response))
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        print("test_get_myprofile_all_data_with_total_objects done")

    def test_03_get_myprofile_all_data_with_errors_none(self):
        user = self.create_user_for_test(
            user_type="CAREMANAGER", email="mongo343@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.create_myprofile()
        response = self.client.get(self.endpoint)

        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.data.get("message"), "success")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("errors"), None)
        print("test_get_myprofile_all_data_with_errors_none")

    def test_04_get_myprofile_none_data_with_message_failed(self):
        user = self.create_user_for_test(
            user_type="CAREMANAGER", email="farhandb34@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        response = self.client.get(self.endpoint)

        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get("message"), "success")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("message"), "failed")
        print("test_get_myprofile_none_data_with_message_failed")

    def test_05_get_myprofile_none_data_with_errors_none(self):
        user = self.create_user_for_test(
            user_type="CAREMANAGER", email="farhandb3@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        response = self.client.get(self.endpoint)
        response_error = response.data.get("errors")["non_field_errors"]

        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get("message"), "success")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_error, ["failed"])
        print("test_get_myprofile_none_data_with_errors_none")

    def test_06_get_myprofile_none_data_with_data_none(self):
        user = self.create_user_for_test(
            user_type="CAREMANAGER", email="farhandb36@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        response = self.client.get(self.endpoint)

        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get("message"), "success")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("data"), None)
        print("test_get_myprofile_none_data_with_data_none")

    def test_07_post_myprofile_with_message_success(self):
        user = self.create_user_for_test(
            user_type="CAREMANAGER", email="farhandb37@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        profile_data = {
            "first_name": "Tanusha",
            "last_name": "Goyal",
            "phone_no": "6260336626",
        }
        response = self.client.post(self.endpoint, profile_data, format="json")
        myprofile_01 = MyProfile.objects.all()[0]

        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        print("test_post_myprofile_with_message_success")

    def test_08_post_myprofile_with_errors_none(self):
        user = self.create_user_for_test(
            user_type="CAREMANAGER", email="farhandb38@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        profile_data = {
            "first_name": "George",
            "last_name": "Golesi",
            "phone_no": "6260336626",
        }
        response = self.client.post(self.endpoint, profile_data, format="json")
        myprofile_01 = MyProfile.objects.all().last()
        response_myprofile = response.data.get("data")

        self.assertEqual(myprofile_01.id, response_myprofile["id"])
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("errors"), None)
        print("test_post_myprofile_with_errors_none")

    def test_09_post_myprofile_with_data_invalid_and_errors_none(self):
        user = self.create_user_for_test(
            user_type="SUPERADMIN", email="farhandb39@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        profile_data = {"last_name": "Golesi", "phone_no": "6260336626"}
        response = self.client.post(self.endpoint, profile_data, format="json")

        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get("message"), "success")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("message"), "failed")
        print("test_post_myprofile_with_data_invalid_and_errors_none")

    def test_10_post_myprofile_with_data_invalid_and_data_none(self):
        user = self.create_user_for_test(
            user_type="SUPERADMIN", email="farhandb40@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        profile_data = {"last_name": "Golesi", "phone_no": "6260336626"}
        response = self.client.post(self.endpoint, profile_data, format="json")

        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get("message"), "success")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("data"), None)
        print("test_post_myprofile_with_data_invalid_and_data_none done")


class TestMyProfileViewDetails(BaseHelperTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_01_get_myprofile_details_all_data_with_message(self):
        user = self.create_user_for_test(
            user_type="CAREMANAGER", email="mongodb4844@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.create_myprofile()
        myprofile = MyProfile.objects.all().last()
        endpoint = f"/api/v1/authentication/my_profile/{myprofile.id}/"
        response = self.client.get(endpoint)
        response_last_myprofile = response.data.get("data")

        self.assertEqual(response_last_myprofile[0]["id"], myprofile.id)
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        print("test_get_myprofile_details_all_data_with_message done")

    def test_02_get_myprofile_details_all_data_with_errors(self):
        user = self.create_user_for_test(
            user_type="CAREMANAGER", email="mongodb4845@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.create_myprofile()
        myprofile = MyProfile.objects.all().last()
        endpoint = f"/api/v1/authentication/my_profile/{myprofile.id}/"
        response = self.client.get(endpoint)
        response_last_myprofile = response.data.get("data")

        self.assertEqual(response_last_myprofile[0]["id"], myprofile.id)
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("errors"), None)
        print("test_get_myprofile_details_all_data_with_errors")

    def test_get_myprofile_details_none_data_with_message(self):
        user = self.create_user_for_test(
            user_type="CAREMANAGER", email="mongodb4846@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.create_myprofile()
        my_profile_id = 100
        endpoint = f"/api/v1/authentication/my_profile/{my_profile_id}/"
        response = self.client.get(endpoint)
        response_error = response.data.get("errors")["non_field_errors"]

        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get("message"), "success")
        self.assertEqual(response_error, ["failed"])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("message"), "failed")
        print("test_get_myprofile_details_none_data_with_message")

    def test_update_myprofile_details_data_with_message(self):
        user = self.create_user_for_test(
            user_type="CAREMANAGER", email="mongodb4847@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.create_myprofile()
        updated_myprofile_data = {
            "first_name": "Yogesh",
            "last_name": "Bhatt",
            "phone_no": "6260229944",
        }
        myprofile = MyProfile.objects.all().last()
        endpoint = f"/api/v1/authentication/my_profile/{myprofile.id}/"
        response = self.client.put(endpoint, updated_myprofile_data, format="json")

        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        print("test_update_myprofile_details_data_with_message")

    def test_update_myprofile_details_data_with__failed_message(self):
        user = self.create_user_for_test(
            user_type="CAREMANAGER", email="mongodb4848@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.create_myprofile()
        updated_myprofile_data = {
            "first_name": "Yogesh",
            "last_name": "Bhatt",
            "phone_no": "6260229944",
        }
        my_profile = MyProfile.objects.all().first()
        endpoint = f"/api/v1/authentication/my_profile/{my_profile.id}0/"
        response = self.client.put(endpoint, updated_myprofile_data, format="json")

        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get("message"), "success")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("message"), "failed")
        print("test_update_myprofile_details_data_with__failed_message")

    def test_delete_myprofile_details_data_with_success_message(self):
        user = self.create_user_for_test(
            user_type="SUPERADMIN", email="mongodb4849@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.create_myprofile()
        myprofile = MyProfile.objects.all().last()
        endpoint = f"/api/v1/authentication/my_profile/{myprofile.id}/"
        response = self.client.delete(endpoint)

        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        print("test_delete_myprofile_details_data_with_success_message done")

    def test_delete_myprofile_details_data_with_failed_message(self):
        user = self.create_user_for_test(
            user_type="SUPERADMIN", email="mongodb4850@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.create_myprofile()
        myprofile = MyProfile.objects.all().last()
        endpoint = f"/api/v1/authentication/my_profile/{myprofile.id}/"
        response = self.client.delete(endpoint)

        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.data.get("message"), "success")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("data"), None)
        self.assertEqual(response.data.get("errors"), None)
        print("test_delete_myprofile_details_data_with_failed_message")


class TestUpdateUserProfileImageView(BaseHelperTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_update_myprofile_image_with_message(self):
        user = self.create_user_for_test(
            user_type="SUPERADMIN", email="mongodb4844@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        image_file = self.generate_photo_file()
        endpoint = f"/api/v1/authentication/update/profile_pic/{user.id}/"
        response = self.client.put(
            endpoint, {"profile_pic": image_file}, format="multipart"
        )

        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        print("test_update_myprofile_image_with_message")

    def test_update_myprofile_image_with_errors_none(self):
        user = self.create_user_for_test(
            user_type="SUPERADMIN", email="mongodb4845@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        image_file = self.generate_photo_file()
        endpoint = f"/api/v1/authentication/update/profile_pic/{user.id}/"
        response = self.client.put(
            endpoint, {"profile_pic": image_file}, format="multipart"
        )
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("errors"), None)
        print("test_update_myprofile_image_with_errors_none done")

    def test_update_myprofile_image_with_profile_pic(self):
        user = self.create_user_for_test(
            user_type="SUPERADMIN", email="mongodb4845@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        image_file = self.generate_photo_file()
        endpoint = f"/api/v1/authentication/update/profile_pic/{user.id}/"
        response = self.client.put(
            endpoint, {"profile_pic": image_file}, format="multipart"
        )
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("errors"), None)
        print("test_update_myprofile_image_with_errors")

    def test_update_myprofile_image_with_message_fail(self):
        user = self.create_user_for_test(
            user_type="SUPERADMIN", email="mongodb4845@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        image_file = self.generate_photo_file()
        endpoint = f"/api/v1/authentication/update/profile_pic/{user.id}0/"
        response = self.client.put(
            endpoint, {"profile_pic": image_file}, format="multipart"
        )
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "success")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data.get("message"), "failed")
        print("test_update_myprofile_image_with_message_fail")


class TestChangePassword(BaseHelperTestCase):
    def setUp(self):
        self.client = APIClient()
        self.endpoint = "/api/v1/authentication/change/password/"

    def test_update_user_password_with_message(self):
        user = self.create_user_for_test(
            user_type="SUPERADMIN", email="mongodb4842@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        update_password = {
            "old_password": "Myadmin123",
            "new_password": "Myadmin12345",
            "confirm_password": "Myadmin12345",
        }
        response = self.client.put(self.endpoint, update_password, format="json")
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "failed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "success")
        print("test_update_user_password_with_message")

    def test_update_user_password_with_wrong_old_password(self):
        user = self.create_user_for_test(
            user_type="SUPERADMIN", email="mongodb4843@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        update_password = {
            "old_password": "Myadmin12",
            "new_password": "Myadmin12345",
            "confirm_password": "Myadmin12345",
        }
        response = self.client.put(self.endpoint, update_password, format="json")
        response_error = response.data.get("errors")["non_field_errors"]
        self.assertNotEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(response.data.get("message"), "success")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data.get("message"), "failed")
        self.assertEqual(response_error, ["Old Password Does Not Match!"])
        print("test_update_user_password_with_wrong_old_password")

    def test_update_user_password_with_mismatch_password(self):
        user = self.create_user_for_test(
            user_type="SUPERADMIN", email="mongodb4844@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        update_password = {
            "old_password": "Myadmin123",
            "new_password": "Myadmin123",
            "confirm_password": "Myadmin12345",
        }
        response = self.client.put(self.endpoint, update_password, format="json")
        response_error = response.data.get("errors")["non_field_errors"]
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get("message"), "success")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data.get("message"), "failed")
        self.assertEqual(response_error, ["Password does not match."])
        print("test_update_user_password_with_mismatch_password")

    def test_update_user_password_with_wrong_new_password(self):
        user = self.create_user_for_test(
            user_type="SUPERADMIN", email="mongodb4844@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        update_password = {
            "old_password": "Myadmin123",
            "new_password": "Myad",
            "confirm_password": "Myad",
        }
        response = self.client.put(self.endpoint, update_password, format="json")
        response_error = response.data.get("errors")["non_field_errors"]
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get("message"), "success")
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data.get("message"), "failed")
        self.assertEqual(
            response_error, ["The password must be at least 8 characters."]
        )
        print("test_update_user_password_with_wrong_new_password")

    def test_update_user_password_with_no_old_password(self):
        user = self.create_user_for_test(
            user_type="SUPERADMIN", email="mongodb4845@gmail.com"
        )
        token = self.user_login(email=user.email)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        update_password = {
            "new_password": "Myadmin12345",
            "confirm_password": "Myadmin12345",
        }
        response = self.client.put(self.endpoint, update_password, format="json")
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data.get("message"), "success")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("message"), "failed")
        print("test_update_user_password_with_no_old_passwordl")
