import io
from PIL import Image

from rest_framework.test import APIClient

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from apps.authentication.models import MyProfile, User
from apps.patient.models import Patient, ScreeningName
from apps.hospital.models import Hospital
from apps.account_manager.models import CareManager

client = APIClient()

class BaseHelperTestCase(TestCase):

    def create_user_for_test(self, user_type, email):
        User = get_user_model()
        user = User.objects.create(
            first_name="John",
            last_name="Doe",
            email=email,
            is_staff=True,
            is_superuser=True,
            user_type=user_type
        )
        user.set_password('Myadmin123')
        user.save()
        return user

    def create_myprofile(self):
        user = self.create_user_for_test(user_type='CAREMANAGER', email='farhandj@gmail.com')
        token = self.user_login(user.email)
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        endpoint = '/api/v1/authentication/my_profile/'
        response_01 = client.post(
            endpoint,
            {"first_name":"Alok", "last_name":'Pandya', 'phone_no':'6260336626'},
            format='json'
        )
        response_02 = client.post(
            endpoint,
            {"first_name":"Ravi", "last_name":'Soni', 'phone_no':'6260336626'},
            format='json'
        )
        response_03 = client.post(
            endpoint,
            {"first_name":"Raju", "last_name":'Jain', 'phone_no':'9074606891'},
            format='json'
        )

    def user_login(self, email):
        login_data = {
            'email': email,
            'password' : 'Myadmin123'
        }
        response = self.client.post(
            reverse('user-login'),
            login_data,
            format='json'
        )
        token = response.data.get('data')['tokens']
        return token

    def create_hospital(self):
        user = self.create_user_for_test(user_type='CAREMANAGER', email='pratik@gmail.com')
        token = self.user_login(user.email)
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        hospital_data = {
            'npi_id':'5448',
            'hospital_name':'MYH Hospital',
            'hospital_tax_id':'434',
            'contact_person_name':'Ashwin Dsouza',
            'email_id':'prakkhar@gmail.com',
            'contact_number':'6260336626',
            'address_1':'Dindayal Nagar, Ratlam',
            'address_2':'Sudama Nagar',
            'state_province_area':'Ratlam',
            'zip_code':'0731',
            'city':'Ratlam',
            'multiple_branch':True,
            'website_url':'www.google.com',
            'hospital_status':True,
            'taxonomy_id':'454',
            'taxonomy_description':'Hospital Tax'
        }
        response = client.post(
            reverse('hospital'),
            hospital_data,
            format='json'
        )

    def generate_photo_file(self):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def create_care_manager(self):
        user = self.create_user_for_test(user_type='CAREMANAGER', email='pratul@gmail.com')
        token = self.user_login(user.email)
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        # self.create_hospital()
        hospital = Hospital.objects.all().last()
        care_manager_data = {
            "email": "hasns@gmail.com", "first_name": "Abisha", "last_name": "Soni",
            "password": "Myadmin1234", "hospital": hospital.id,
            "contact": "6260336626", "address": "Dindayal Nagar",
            "care_manager_data": "ACTIVE", "secondary_email": "padun@gmail.com",
            "secondary_contact": "8989466293"
        }
        endpoint = '/api/v1/account/manager/caremanager/'
        response = client.post(
            endpoint,
            care_manager_data,
            format='json'
        )

    def create_patient(self):
        user = self.get_user()
        self.create_hospital()
        hospital = self.get_hospital()

        Patient.objects.create(
            user=user,
            hospital=hospital,
            title='Trimurti',
            middle_name='Singh',
            dob='1996-04-22',
            gender="MALE",
            patient_status="ACTIVE",
        )

    def create_screening_name(self):

        ScreeningName.objects.create(name='Blodd Pressure')
        ScreeningName.objects.create(name='Medical Nutrition Therapy')
        ScreeningName.objects.create(name="Abdominal Aortic Aneurysm")
        ScreeningName.objects.create(name="Alcohol Misuse and  Counseling")
        ScreeningName.objects.create(name="Bone Density Measurement")
        ScreeningName.objects.create(name="Cardiovascular Screenings  (total cholesterol, LDL, HDL)")
        ScreeningName.objects.create(name="Colorectal Cancer - Stool sample")
        ScreeningName.objects.create(name="Colorectal Cancer - Flexible sigmoidoscopy")
        ScreeningName.objects.create(name="Colorectal Cancer - Screening colonoscopy")
        ScreeningName.objects.create(name="Depression")
        ScreeningName.objects.create(name="Diabetes Screening and   Self-Management Training")
        ScreeningName.objects.create(name="Glaucoma")
        ScreeningName.objects.create(name="HIV")
        ScreeningName.objects.create(name="Mammogram")
        ScreeningName.objects.create(name="Medical Nutrition Therapy")
        ScreeningName.objects.create(name="Obesity and Counseling")
        ScreeningName.objects.create(name="Pap Smear and  Pelvic Exam")
        ScreeningName.objects.create(name="Prostate Cancer")
        ScreeningName.objects.create(name="Tobacco Use Counseling")
        ScreeningName.objects.create(name="Vaccines - Hepatitis B")
        ScreeningName.objects.create(name="Vaccines - Hepatitis B")
        
        # response = client.post(
        #     endpoint,
        #     care_manager_data,
        #     format='json'
        # )

    def get_caremanager(self):
        care_manager = CareManager.objects.all().last()
        return care_manager

    def get_user(self):
        user = User.objects.all().last()
        return user

    def get_hospital(self):
        hospital = Hospital.objects.all().last()
        return hospital
