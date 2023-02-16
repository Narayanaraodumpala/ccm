import os
import threading
import secrets
import string
from datetime import date
from threading import Thread

import django_filters
from random import randint
from django.db import models
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.utils.encoding import smart_bytes
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django_filters import OrderingFilter, filters, DateFromToRangeFilter

from apps.account_manager.models import PracticeAdmin, Provider, CareManager, Patient, PatientProviderMapping
from apps.hospital.models import Hospital
from apps.patient.models import CareManagerNotes, PatientOutreach, PatientCallLog, Task, Goal

from rest_framework.test import APITestCase
from rest_framework.filters import SearchFilter



User = get_user_model()


class Validator:
    def is_valid_user(email, password, system_id=None, request=None):
        try:
            if system_id is not None:
                obj = User.objects.filter(system_id=system_id).last()
                email = obj.email
                user = authenticate(email=email, password=password)
                login(request, user)
            else:
                user = authenticate(email=email, password=password)
                login(request, user)
            if not user:
                return False, "Invalid credentials, please try again.", None
        except Exception as e:
            message = "Invalid credentials"
            return False, message, None
        return True, "success", user.email

    def get_user_instance(email):
        try:
            superuser = User.objects.filter(
                email=email, is_superuser=True, is_staff=True, is_active=True
            ).last()
            practiceadmin = PracticeAdmin.objects.filter(user__email=email).last()
            provider = Provider.objects.filter(user__email=email).last()
            caremanager = CareManager.objects.filter(user__email=email).last()
            patient = Patient.objects.filter(user__email=email).last()

            if superuser:
                user_type = superuser.user_type
                return superuser, user_type
            if practiceadmin:
                user_type = practiceadmin.user.user_type
                return practiceadmin.user, user_type
            if provider:
                user_type = provider.user.user_type
                return provider.user, user_type
            if caremanager:
                user_type = caremanager.user.user_type
                return caremanager.user, user_type
            if patient:
                user_type = patient.user.user_type
                return patient.user, user_type
            return False, None
        except Exception as e:
            return False, str(e)


class SendMail:
    @staticmethod
    def user_send_password_reset_email(data):
        try:
            uidb64 = urlsafe_base64_encode(smart_bytes(data.id))
            token = PasswordResetTokenGenerator().make_token(data)
            absurl = f"{settings.FE_BASE_URL}/{uidb64}/{token}/"
            data = {
                "url": absurl,
                "user_detail": data,
                "to_email": data.email,
            }
            subject, from_email, to = (
                "Forget password",
                settings.FROM_TO,
                data["to_email"],
            )
            html_content = render_to_string("forgetpassword.html", data)
            # msg = EmailMultiAlternatives(subject, from_email, [to])
            # msg.attach_alternative(html_content, "text/html")
            # msg.send()
            send_mail(
                subject,
                "Testing Mail",
                from_email,
                [to],
                html_message=html_content,
                fail_silently=False,
            )
        except Exception as e:
            print(e)

    @staticmethod
    def user_send_credential_email(data, password):
        try:
            from apps.authentication.models import User
            text_content = "This is an important message."
            user = User.objects.filter(email=data.email).last()

            patient_data = {
                "patient_name": data.first_name,
                "to_email": user.email,
                "password": password,
                "to_email": data.email,
            }
            subject, from_email, to = (
                "For sign up",
                settings.FROM_TO,
                patient_data["to_email"],
            )

            if user.user_type == "PRACTICEADMIN":
                pa = PracticeAdmin.objects.filter(user=user).last()
                user_hospital = pa.hospital.hospital_name
                practiceadmin_data = {
                "practice_admin_name": user.first_name,
                "to_email": user.email,
                "password": password,
                "login_url": settings.LOGIN_URL
                }
                html_content = render_to_string("practice_admin_credentials_mail.html", practiceadmin_data)

                
            elif user.user_type == "CAREMANAGER":
                user_hospital = user.care_users.hospital.hospital_name
                caremanager_data = {
                "caremanager_name": user.first_name,
                "to_email": user.email,
                "password": password,
                "login_url": settings.LOGIN_URL,
                "hospital_name": user_hospital
                
                }
                html_content = render_to_string("caremanager_credential_mail.html", caremanager_data)
            else:
                html_content = render_to_string("patient_credential_mail.html", patient_data)

            # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            # msg.attach_alternative(html_content, "text/html")
            # msg.send()
            send_mail(
                subject,
                text_content,
                from_email,
                [to],
                html_message=html_content,
                fail_silently=False,
            )
        except Exception as e:
            print(e)
    
    @staticmethod
    def user_upadte_credential_email(data, password):
        try: 
            from apps.authentication.models import User
            text_content = "This is an important message."
            user = User.objects.filter(email=data.email).last()
            patient_data = {
                "patient_name": data.first_name,
                "to_email": user.email,
                "password": password,
                "to_email": data.email,
            }
            subject, from_email, to = (
                "For Updated Credentials",
                settings.FROM_TO,
                patient_data["to_email"],
            )

            if user.user_type == "PRACTICEADMIN":
                pa = PracticeAdmin.objects.filter(user=user).last()
                user_hospital = pa.hospital.hospital_name
                practiceadmin_data = {
                "practice_admin_name": user.first_name,
                "to_email": user.email,
                "password": password,
                "login_url": settings.LOGIN_URL
                }
                html_content = render_to_string("practice_update_practice_admin_mail.html",practiceadmin_data)
                
            elif user.user_type == "CAREMANAGER":
                user_hospital = user.care_users.hospital.hospital_name
                caremanager_data = {
                "caremanager_name": user.first_name,
                "to_email": user.email,
                "password": password,
                "login_url": settings.LOGIN_URL,
                "hospital_name": user_hospital
                
                }
                html_content = render_to_string("practice_update_caremanager_mail.html", caremanager_data)
            
            elif user.user_type == "PROVIDER":
                caremanager_data = {
                "provider_name": user.first_name,
                "to_email": user.email,
                "password": password,
                "login_url": settings.LOGIN_URL,
                
                }
                html_content = render_to_string("practice_update_provider_mail.html", caremanager_data)
            else:
                html_content = render_to_string("patient_credential_mail.html", patient_data)

            send_mail(
                subject,
                text_content,
                from_email,
                [to],
                html_message=html_content,
                fail_silently=False,
            )
        except Exception as e:
            print(e)
            
    
    @staticmethod
    def user_send_welcome_email(data):
        try:
            from apps.authentication.models import User
            text_content = "This is an important message."
            user = User.objects.filter(email=data.email).last()

            patient_data = {
                "patient_name": data.first_name,
                "to_email": data.email,
            }
            subject, from_email, to = (
                "Welcome Mail",
                settings.FROM_TO,
                patient_data["to_email"],
            )

            if user.user_type == "PRACTICEADMIN":
                pa = PracticeAdmin.objects.filter(user=user).last()
                user_hospital = pa.hospital.hospital_name
                practiceadmin_data = {
                "practice_admin_name": user.first_name,
                "login_url": settings.LOGIN_URL
                }
                html_content = render_to_string("practice_admin_welcome_mail.html", practiceadmin_data)
                
            elif user.user_type == "CAREMANAGER":
                user_hospital = user.care_users.hospital.hospital_name
                caremanager_data = {
                "caremanager_name": user.first_name,
                "hospital_name": user_hospital                
                }
                html_content = render_to_string("caremanager_welcome_mail.html", caremanager_data)
            else:
                html_content = render_to_string("patient_welcome_mail.html", patient_data)

            # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            # msg.attach_alternative(html_content, "text/html")
            # msg.send()
            send_mail(
                subject,
                text_content,
                from_email,
                [to],
                html_message=html_content,
                fail_silently=False,
            )
        except Exception as e:
            print(e)
            
               
    @staticmethod
    def send_email_patient_from_caremanager(data, password, *args, **kwargs):
        try:
            data = {
                "patient_name": data.first_name,
                "to_email": data.email,
                "password": password,
                "hospital_name": kwargs['hospital_name']    
            }
            subject, from_email, to = (
                "Signup Detail",
                settings.FROM_TO,
                data["to_email"],
            )
            text_content = "This is an important message."
            html_content = render_to_string("patient_registration_from_caremanager.html", data)
            # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            # msg.attach_alternative(html_content, "text/html")
            # msg.send()
            send_mail(
                subject,
                text_content,
                from_email,
                [to],
                html_message=html_content,
                fail_silently=False,
            )
        except Exception as e:
            print(e)
        

    @staticmethod
    def send_welcome_email_provider_from_caremanager(data):
        try:
            data = {
                "provider_name": data.first_name,
                "to_email": data.email,
            }
            subject, from_email, to = (
                "For sign up",
                settings.FROM_TO,
                data["to_email"]
            )
            text_content = "This is an important message."
            html_content = render_to_string("provider_registration_from_caremanager.html", data)
            send_mail(
                subject,
                text_content,
                from_email,
                [to],
                html_message=html_content,
                fail_silently=False,
            )
        except Exception as e:
            print(e)
            
    def send_credential_email_provider_from_caremanager(data, password):
        try:
            data = {
                "provider_name": data.first_name,
                "to_email": data.email,
                "password": password
            }
            subject, from_email, to = (
                "Signup Detail",
                settings.FROM_TO,
                data["to_email"]
            )
            text_content = "This is an important message."
            html_content = render_to_string("provider_credential_from_caremanager.html", data)
            send_mail(
                subject,
                text_content,
                from_email,
                [to],
                html_message=html_content,
                fail_silently=False,
            )
        except Exception as e:
            print(e)        
    
    @staticmethod
    def send_patient_summary_pdf_mail(data, files):
        try:
            subject, from_email, to = (
                data['subject'],
                settings.FROM_TO,
                data['to_mail']
            )
            message = data['message']
            mail = EmailMessage(subject, message, settings.FROM_TO, [to])
            mail.attach(files.name, files.read(), files.content_type)
            mail.send()
        except Exception as e:
            print(e)


def create_related_user(data, user_type: str) -> User:
    if User.objects.filter(email=data["email"]).exists():
        raise ValueError("This Email already exist.")
    profile_pic = data.get("profile_pic", None)
    user = User.objects.create(
        email=data["email"], first_name=data["first_name"], last_name=data["last_name"], profile_pic=profile_pic
    )
    user.set_password(data["password"])
    user.user_type = user_type
    user.username = None
    user.save()

    return user


def create_provider_user(data, user_type: str) -> User:
    if User.objects.filter(email=data["email"]).exists():
        raise ValueError("This Email already exist.")
    first_name = data.get("first_name", None)
    last_name = data.get("last_name", None)
    profile_pic = data.get("profile_pic", None)
    user = User.objects.create(
        email=data["email"], first_name=first_name, last_name=last_name,
        profile_pic=profile_pic
    )
    user.set_password(data["password"])
    user.user_type = user_type
    user.username = None
    user.save()
    return user


def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


def create_provider_user_for_care_manager(data, user_type: str) -> User:
    password = auto_generate_password()
    profile_pic = data.get("profile_pic", None)

    if data["email"] == "":
        random_email = str(random_with_N_digits(4)) + '.' + str(data["first_name"]) + '.' + str(data["last_name"]) + '@gmail.com'
        user = User.objects.create(
            email=random_email, first_name=data["first_name"], last_name=data["last_name"], profile_pic=profile_pic, user_type=user_type
        )
    else:
        if User.objects.filter(email=data["email"]).exists():
            raise ValueError("This Email already exist.")
        password = auto_generate_password()
        profile_pic = data.get("profile_pic", None)
        user = User.objects.create(
            email=data["email"], first_name=data["first_name"], last_name=data["last_name"], profile_pic=profile_pic, user_type=user_type
        )
    return user, password


def create_patient_user_for_care_manager(data, user_type: str) -> User:
    profile_pic = data.get("profile_pic", None)

    if data["email"] == "":
        random_email = str(random_with_N_digits(4)) + '.' + str(data["first_name"]) + '.' + str(data["last_name"]) + '@gmail.com'
        user = User.objects.create(
            email=random_email, first_name=data["first_name"], last_name=data["last_name"], profile_pic=profile_pic
        )
    else:
        if User.objects.filter(email=data["email"]).exists():
            raise ValueError("This Email already exist.")
        user = User.objects.create(
            email=data["email"], first_name=data["first_name"], last_name=data["last_name"], profile_pic=profile_pic
        )
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))
    user.set_password(password)
    user.user_type = user_type
    user.username = None
    user.save()
    return user, password


def auto_generate_password():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))
    return password


def calculate_patient_age(patient):
    age = 0
    try:
        if patient:
            if patient.dob:
                today = date.today()
                patient_dob = patient.dob
                age = today.year - patient_dob.year - ((today.month, today.day) < (patient_dob.month, patient_dob.day))
            else:
                pass
    except Exception as e:
        print(str(e))
    return age

def get_patient_full_name(patient):
    full_name = None
    try:
        if patient.user:
            full_name = patient.user.get_full_name()
    except Exception as e:
        print(str(e))
    return full_name

def get_patient_id(patient):
    patient_id = None
    try:
        if patient:
            patient_id = patient.id
    except Exception as e:
        print(str(e))
    return patient_id

def get_patient_cell_phone(patient):
    cell_phone = None
    try:
        if patient:
            cell_phone = patient.patient_contact_detail.all()
            for number in cell_phone:
                return number.cell_phone
    except Exception as e:
        print(str(e))
    return cell_phone

# def build_task_data(tasks):
#     task_list = []
#     try:
#         for task_obj in tasks:
#             data = {}
#             if task_obj.__class__ == Task:
#                 data['task_name'] = task_obj.name
#                 data['task_type'] = 'Task'
#                 data['task_status'] = task_obj.task_status
#                 data['patient_age'] = calculate_patient_age(task_obj.patient)
#                 data['patient_name'] = get_patient_full_name(task_obj.patient)
#                 data['patient_id'] = get_patient_id(task_obj.patient)
#             elif task_obj.__class__ == Goal:
#                 data['task_name'] = task_obj.name
#                 data['task_type'] = "Goal"
#                 data['task_status'] = task_obj.goal_status
#                 data['patient_age'] = calculate_patient_age(task_obj.patient)
#                 data['patient_name'] = get_patient_full_name(task_obj.patient)
#                 data['patient_id'] = get_patient_id(task_obj.patient)
#             elif task_obj.__class__ == PatientOutreach:
#                 data['task_name'] = task_obj.notes
#                 data['task_type'] = 'Outreach'
#                 data['task_status'] = task_obj.outreach_status
#                 data['patient_age'] = calculate_patient_age(task_obj.patient)
#                 data['patient_name'] = get_patient_full_name(task_obj.patient)
#                 data['patient_id'] = get_patient_id(task_obj.patient)

#             data['created_at'] = task_obj.created_at
#             data['updated_at'] = task_obj.modified_at
#             task_list.append(data)
#         task_list = sorted(task_list, key=lambda d: d['updated_at'], reverse=True) 
#         return task_list
#     except Exception as e:
#         print(e)
#         return task_list


class PatientListFilter(django_filters.FilterSet):
    # minutes_completed = django_filters.CharFilter(label="minutes_completed")

    from_date = filters.DateFilter(field_name='created_at', label='from_date', lookup_expr='date__gte')
    to_date = filters.DateFilter(field_name='created_at', label='to_date', lookup_expr='date__lte')

    # unassigned_providers = django_filters.CharFilter(label='unassigned-providers', method='blank_providers')
    # all_patient = filters.CharFilter(label='all_patient', method='blank_all_patient')

    filter_provider = filters.CharFilter(label='Search Provider', method='providers_search')
    # patient_name = filters.CharFilter(label='Search Patient', method='patient_search')

    # def blank_providers(self, queryset, value, *args, **kwargs):
    #     try:
    #         if value == "unassigned_providers":
    #             patient_ids = queryset.values_list('id',flat=True)
    #             ppm = PatientProviderMapping.objects.filter(patient_id__in=patient_ids)
    #             ppm_patient_list = ppm.values_list('patient_id', flat=True)
    #             queryset = queryset.exclude(id__in=ppm_patient_list)
    #     except ValueError:
    #         pass
    #     return queryset
    
    # def blank_all_patient(self,queryset, value,*args, **kwargs):
    #     try:
    #         if value == "all_patient":
    #             return Patient.objects.all()
           
    #     except ValueError:
    #         pass
    #     return queryset    

    def providers_search(self, queryset, value, *args, **kwargs):
        try:
            if value == "filter_provider":
                provider_name = self.request.GET.get('filter_provider', None)
                patient_ids = queryset.values_list('id', flat=True)
                ppm = PatientProviderMapping.objects.filter(patient_id__in=patient_ids, primary_provider__user__first_name__icontains=provider_name)
                ppm_patient_list = ppm.values_list('patient_id', flat=True)
                queryset = queryset.filter(id__in=ppm_patient_list)
        except ValueError:
            pass
        return queryset


    order_by_field = 'ordering'
    ordering = OrderingFilter(
        # fields (('model field name', 'parameter name'),)
        fields=
        (
            ('id', 'id'),
            ('user__first_name', 'patient_name'),
            ('created_at', 'created_at'),
        )
        )
    class Meta:
        model = Patient
        fields = ['id']


class HospitalFilter(django_filters.FilterSet):
    from_date = filters.DateFilter(field_name='created_at', label='from_date', lookup_expr='date__gte')
    to_date = filters.DateFilter(field_name='created_at', label='to_date', lookup_expr='date__lte')
    
    order_by_field = 'ordering'
    ordering = OrderingFilter(
        fields=(
            ("id", "ID"),
            ("hospital_name", "hospital_name"),
            ("npi_id", "npi_id"),
            ("address_1", "address_1"),
            ("created_at", "created_at"),
        ),
    )
    
    class Meta:
        model = Hospital
        fields = ['id', 'hospital_name', 'npi_id', 'address_1']
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }

        

class PatientOutreachFilter(django_filters.FilterSet):
    # contact_date = django_filters.CharFilter(lookup_expr = 'icontains', label="contact date")
    # schedule_follow_up_date = django_filters.CharFilter(lookup_expr = 'icontains', label="schedule follow up date")
    # contact_type = django_filters.CharFilter(lookup_expr = 'icontains', label="contact type")
    # resolution_action = django_filters.CharFilter(lookup_expr = 'icontains', label="resolution action")
    # time_spent = django_filters.CharFilter(lookup_expr = 'icontains', label="time spent")
 
    
    order_by_field = 'ordering'
    ordering = OrderingFilter(
        fields=(
            ("id", "id"),
            ("contact_date", "contact_date"),
            ("schedule_follow_up_date", "schedule_follow_up_date"),
            ("contact_type", "contact_type"),
            ("resolution_action", "resolution_action"),
            ("time_spent", "time_spent"),
            ("patient__user__first_name", "patient_name"),
            ("outcome", "outcome"),

        ),
    )
    
    class Meta:
        model = PatientOutreach
        fields = ['id', 'contact_date', 'schedule_follow_up_date', 'contact_type', 'resolution_action', 'outcome', 'time_spent']


class ProviderFilter(django_filters.FilterSet):
    from_date = filters.DateFilter(field_name='created_at', label='from_date', lookup_expr='date__gte')
    to_date = filters.DateFilter(field_name='created_at', label='to_date', lookup_expr='date__lte')

    order_by_field = 'ordering'
    ordering = OrderingFilter(
        fields=(
            ("id", "id"),
            ("user__first_name", "provider_name"),
            ("gender", "gender"),
            ("created_at", "created_at")
        ),
    )

    class Meta:
        model = Provider
        fields = ['id', 'created_at']
        
        
class PatientFilter(django_filters.FilterSet):
    from_date = filters.DateFilter(field_name='created_at', label='from_date', lookup_expr='gte')
    to_date = filters.DateFilter(field_name='created_at', label='to_date', lookup_expr='lte')

    order_by_field = 'ordering'
    ordering = OrderingFilter(
        fields=(
            ("id", "id"),
            ("created_at", "created_at")
        ),
    )
    class Meta:
        model = PatientCallLog
        fields = ['id', 'created_at']



def build_task_data(tasks):
    task_list = []
    try:
        if tasks:
            for task_obj in tasks:
                data = {}
                if task_obj.__class__ == Task:
                    data['id'] = task_obj.id
                    data['task_name'] = task_obj.name
                    data['task_type'] = 'Task'
                    data['task_status'] = task_obj.task_status
                    data['patient_age'] = calculate_patient_age(task_obj.patient)
                    data['patient_name'] = get_patient_full_name(task_obj.patient)
                    data['patient_id'] = get_patient_id(task_obj.patient)
                    if task_obj.time_spent:
                        data['time_spent'] = task_obj.time_spent.seconds // 60
                    else:
                        data['time_spent'] = 00
                    data['notes'] = task_obj.notes
                    data['date'] = task_obj.task_date  
                    # data['recurrence_pattern'] = task_obj.recurrence_pattern
                    data['from_date'] = task_obj.from_date
                    data['to_date'] = task_obj.to_date
                    # data['recurrence_pattern'] = task_obj.recurrence_pattern  
                    data['cell_phone'] = get_patient_cell_phone(task_obj.patient)
                    data['follow_up_date'] = task_obj.follow_up_date                       
                    
                elif task_obj.__class__ == PatientOutreach:
                    data['id'] = task_obj.id
                    data['task_name'] = task_obj.outreach_name
                    data['task_type'] = 'Intervention'
                    data['task_status'] = task_obj.outreach_status
                    data['patient_age'] = calculate_patient_age(task_obj.patient)
                    data['patient_name'] = get_patient_full_name(task_obj.patient)
                    data['patient_id'] = get_patient_id(task_obj.patient)
                    if task_obj.time_spent:
                        data['time_spent'] = task_obj.time_spent.seconds // 60               
                    else:
                        data['time_spent'] = 00
                    data['notes'] = task_obj.notes 
                    data['contact_date'] = task_obj.contact_date
                    data['follow_up_date'] = task_obj.schedule_follow_up_date
                    data['contact_type'] = task_obj.contact_type 
                    data['resolution_action'] = task_obj.resolution_action
                    data['outcome'] = task_obj.outcome  
                    data['care_program_from_date'] = task_obj.care_program_from_date
                    data['care_program_to_date'] = task_obj.care_program_to_date  
                    data['cell_phone'] = get_patient_cell_phone(task_obj.patient)                          
                    
                    
                elif task_obj.__class__ == CareManagerNotes:
                    data['id'] = task_obj.id
                    data['task_type'] = 'Notes'
                    data['task_status'] = task_obj.cm_notes_status
                    data['patient_age'] = calculate_patient_age(task_obj.patient)
                    data['patient_name'] = get_patient_full_name(task_obj.patient)
                    data['patient_id'] = get_patient_id(task_obj.patient)
                    if task_obj.time_spent:
                        data['time_spent'] = task_obj.time_spent.seconds // 60             
                    else:
                        data['time_spent'] = 00
                    data['notes'] = task_obj.notes    
                    data['chronic_condition'] = task_obj.chronic_condition   
                    data['cell_phone'] = get_patient_cell_phone(task_obj.patient)                          
                                    

                data['created_at'] = task_obj.created_at
                data['updated_at'] = task_obj.modified_at
                task_list.append(data)
            task_list = sorted(task_list, key=lambda d: d['updated_at'], reverse=True) 
        return task_list
    except Exception as e:
        print(e)
        return task_list



def build_calllog_data(tasks):
    task_list = []
    try:
        if tasks:
            for task_obj in tasks:
                data = {}
                if task_obj.__class__ == Task:
                    data['id'] = task_obj.id
                    data['task_name'] = task_obj.name
                    data['task_type'] = 'Task' 
                    data['task_status'] = task_obj.task_status 
                    data['patient_age'] = calculate_patient_age(task_obj.patient)
                    data['patient_name'] = get_patient_full_name(task_obj.patient)
                    data['patient_id'] = get_patient_id(task_obj.patient)
                    if task_obj.time_spent:
                        data['time_spent'] = task_obj.time_spent.seconds // 60
                    else:
                        data['time_spent'] = 00
                    data['notes'] = task_obj.notes 
                    data['date'] = task_obj.task_date                             
                    
                elif task_obj.__class__ == PatientOutreach:
                    data['id'] = task_obj.id
                    data['task_name'] = task_obj.outreach_name
                    data['task_type'] = 'Intervention'
                    data['task_status'] = task_obj.outreach_status
                    data['patient_age'] = calculate_patient_age(task_obj.patient)
                    data['patient_name'] = get_patient_full_name(task_obj.patient)
                    data['patient_id'] = get_patient_id(task_obj.patient)
                    if task_obj.time_spent:
                        data['time_spent'] = task_obj.time_spent.seconds // 60 
                    else:
                        data['time_spent'] = 00              
                    data['notes'] = task_obj.notes 
                    
                elif task_obj.__class__ == PatientCallLog:
                    data['id'] = task_obj.id
                    data['call_type'] = task_obj.call_type
                    data['call_status'] = task_obj.call_status
                    data['patient_age'] = calculate_patient_age(task_obj.patient)
                    data['patient_name'] = get_patient_full_name(task_obj.patient)
                    data['patient_id'] = get_patient_id(task_obj.patient)
                    data['call_duration'] = task_obj.call_duration                
                    data['agenda'] = task_obj.agenda  
                    data['call_meet_link'] = task_obj.call_meet_link 
                    data['call_start_datetime'] = task_obj.call_start_datetime 
                    data['call_end_datetime'] = task_obj.call_end_datetime 
                
                elif task_obj.__class__ == CareManagerNotes:
                    data['id'] = task_obj.id
                    data['task_type'] = 'Notes'
                    data['task_status'] = task_obj.cm_notes_status
                    data['patient_age'] = calculate_patient_age(task_obj.patient)
                    data['patient_name'] = get_patient_full_name(task_obj.patient)
                    data['patient_id'] = get_patient_id(task_obj.patient)
                    if task_obj.time_spent:
                        data['time_spent'] = task_obj.time_spent.seconds // 60 
                    else:
                        data['time_spent'] = 00 
                    data['notes'] = task_obj.notes    
                    data['chronic_condition'] = task_obj.chronic_condition                                                     
                data['created_at'] = task_obj.created_at
                data['updated_at'] = task_obj.modified_at
                task_list.append(data)
            task_list = sorted(task_list, key=lambda d: d['updated_at'], reverse=True) 
        return task_list
    except Exception as e:
        print(e)
        return task_list
    
class TaskFilter(django_filters.FilterSet):

    order_by_field = 'ordering'
    ordering = OrderingFilter(
        fields=(
            ("id", "id"),
            ("task_status", "task_status"),
            ("resolution_action", "resolution_action"),            
        ),
    )
    class Meta:
        model = Task
        fields = ['id','created_at']    
        
class PatientOutreachFilter(django_filters.FilterSet):

    order_by_field = 'ordering'
    ordering = OrderingFilter(
        fields=(
            ("id", "id"),
            ("outreach_status", "outreach_status"),
            ("contact_type", "contact_type"),            
        ),
    )
    class Meta:
        model = PatientOutreach
        fields = ['id','created_at']       
        

class CareManagerNotesFilter(django_filters.FilterSet):

    order_by_field = 'ordering'
    ordering = OrderingFilter(
        fields=(
            ("id", "id"),
            ("outreach_status", "outreach_status"),
            ("contact_type", "contact_type"),            
        ),
    )
    class Meta:
        model = CareManagerNotes
        fields = ['id','created_at']


class PatientSearchFilter(SearchFilter):
    def get_search_fields(self, view, request):
        if request.query_params.get('search'):
            return ['user__first_name', 'user__last_name', 'patient_contact_detail__cell_phone', 'patient_patientprovidermapping__primary_provider__user__first_name', 'caremanager_obj__user__first_name']


class AssignProviderPatientSearch(SearchFilter):
    def get_search_fields(self, view, request):
        if request.query_params.get('search'):
            return ['primary_provider__user__first_name', 'primary_provider__user__last_name','patient__user__first_name','patient__user__last_name','patient__caremanager_obj__user__first_name', 'patient__caremanager_obj__user__last_name']
class UnAssignProviderPatientSearch(SearchFilter):
    def get_search_fields(self, view, request):
        if request.query_params.get('search'):
            return ['user__first_name', 'user__last_name', 'patient_patientprovidermapping__primary_provider__user__first_name', 'patient_patientprovidermapping__primary_provider__user__last_name']
