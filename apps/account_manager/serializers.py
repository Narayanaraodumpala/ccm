import datetime
from datetime import date
from itertools import chain
from datetime import date, timedelta  
from time import gmtime
from time import strftime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from apps.account_manager.models import PatientProviderMapping, PatientContactDetails,PatientSession
from apps.account_manager.models import (
    CareManager,
    Provider,
    Patient,
    PracticeAdmin,
    Communication,
)
from apps.authentication.serializers import UserSerializer
from apps.hospital.models import PatientChronicDisease, ChronicCondition
from django.forms.models import model_to_dict
from apps.hospital.models import HospitalBranch
from apps.patient.helper import get_user_full_name
from apps.patient.serializers import PatientTreatmentSerializer
from apps.patient.utils import get_mannual_total_time, get_session_total_time, get_session_total_time_current_month, get_mannual_total_time_current_month, get_session_total_time_previous_month, get_mannual_total_time_previous_month
from rest_framework import serializers

from apps.account_manager.utils import build_task_data, create_provider_user
from apps.patient.models import AnnualWellnessVisitCallLog, AssessmentCallLog, CareManagerNotes, MedicalConditionCallLog, PatientCallLog, \
    SelfManagementPlanCallLog, Task, VitalCallLog, Goal, PatientOutreach
from apps.hospital.serializers import HospitalBranchSerializer

from django.db.models import Q
from django.db.models import Value
from django.db.models.functions import Concat


User = get_user_model()


class PatientSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        exclude = ['user']

    def get_profile_pic(self, obj):
        if obj.user.profile_pic:
            return settings.BACKEND_URL + obj.user.profile_pic.url
        else:
            return None


class CareManagerSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField(required=False)
    hospital_branch = serializers.SerializerMethodField(required=False)

    class Meta:
        model = CareManager
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "contact",
            "address",
            "hospital",
            "profile_pic",
            "care_manager_status",
            "hospital_branch",
            "secondary_email",
            "secondary_contact",
        ]

    def validate(self, data):
        if data.get("hospital_branch"):
            hospital_branches = data.get("hospital_branch")
            for hospital_branch in hospital_branches:
                hospital_branchs = HospitalBranch.objects.filter(pk=hospital_branch)
                for hospital_branch in hospital_branchs:
                    if hospital_branch.care_manager:
                        raise Exception(f"Location is already assigned to {hospital_branch.care_manager.user.first_name} {hospital_branch.care_manager.user.first_name}") 
                    else:
                        continue            
            return data  
        else:
            return data


    def get_email(self, obj):
        return obj.user.email

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_profile_pic(self, obj):
        try:
            if obj.user.profile_pic:
                return settings.BACKEND_URL + obj.user.profile_pic.url
            else:
                return None
        except:
            return None

    def get_hospital_branch(self, obj):
        try:
            # hospital_branches = obj.hospital.hospital_branch.all()
            hospital_branches = []
            data = HospitalBranch.objects.filter(care_manager=obj)
            if data:
                hospital_branches = HospitalBranchSerializer(data, many=True)
            return hospital_branches.data
            # hospital_branch_list = [model_to_dict(hospital_branch) for hospital_branch in hospital_branches]
        except:
            hospital_branch_list = []
        return hospital_branch_list


class PracticeAdminSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    password = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = PracticeAdmin
        fields = ["id", "hospital", "first_name", "last_name", "email", "contact_number", "password", "profile_pic",
                  "practice_admin_status"]

    def get_email(self, obj):
        return obj.user.email

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_password(self, obj):
        return obj.user.password

    def get_profile_pic(self, obj):
        if obj.user.profile_pic:
            return settings.BACKEND_URL + obj.user.profile_pic.url
        else:
            return None


class ProviderHospitalBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalBranch
        fields = "__all__"
        
class ProviderCreateSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    password = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()
    hospital_branch = serializers.SerializerMethodField(required=False)
        
    class Meta:
        model = Provider
        fields = [
            "id",
            "npi_data",
            "hospital",
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "password",
            "contact_number",
            "provider_status",
            "profile_pic",
            "hospital_branch",
            "zip_code",
            "taxonomy_description",
            "taxonomy_code_set",
            "taxonomy_code",
        ]
        
    def validate(self, data):           
            if data.get("hospital_branch"):
                hospital_branches = data.get("hospital_branch")
                for hospital_branch in hospital_branches:
                    hospital_branchs = HospitalBranch.objects.filter(pk=hospital_branch)
                    for hospital_branch in hospital_branchs:
                        if hospital_branch.provider:
                            raise Exception(f"Location is already assigned to {hospital_branch.provider.user.first_name} {hospital_branch.provider.user.first_name}") 
                        else:
                            continue              
                return data  
            else:
                return data  

    def get_email(self, obj):
        return obj.user.email

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_password(self, obj):
        return obj.user.password

    def get_profile_pic(self, obj):
        if obj.user.profile_pic:
            return settings.BACKEND_URL + obj.user.profile_pic.url
        else:
            return None
    
    def get_hospital_branch(self, obj):
        try:
            hospital_branches = obj.hospital_branch_provider.all()
            hospital_branch_list = [model_to_dict(hospital_branch) for hospital_branch in hospital_branches]
        except:
            hospital_branch_list = []
        return hospital_branch_list


class ProviderSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    password = serializers.SerializerMethodField()
    # department = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()
    hospital_branch = serializers.SerializerMethodField()

    class Meta:
        model = Provider
        fields = [
            "id",
            "npi_data",
            "hospital",
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "password",
            "contact_number",
            "provider_status",
            "profile_pic",
            "hospital_branch",
            "zip_code",
            "taxonomy_description",
            "taxonomy_code_set",
            "taxonomy_code",
        ]

    def validate(self, data):           
        if data.get("hospital_branch"):
            hospital_branches = data.get("hospital_branch")
            for hospital_branch in hospital_branches:
                hospital_branchs = HospitalBranch.objects.filter(pk=hospital_branch)
                for hospital_branch in hospital_branchs:
                    if hospital_branch.provider:
                        raise Exception(f"Location is already assigned to {hospital_branch.provider.user.first_name} {hospital_branch.provider.user.first_name}") 
                    else:
                        continue              
            return data  
        else:
            return data

    def get_email(self, obj):
        return obj.user.email

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_password(self, obj):
        return obj.user.password

    # def get_department(self, obj):
    #     breakpoint()
    #     if obj.department:
    #         return obj.department.name
    #     else:
    #         return None

    def get_profile_pic(self, obj):
        if obj.user.profile_pic:
            return settings.BACKEND_URL + obj.user.profile_pic.url
        else:
            return None

    def get_hospital_branch(self, obj):    
        if obj.hospital_branch_provider.all():
            branches = obj.hospital_branch_provider.all()            
            branches= [model_to_dict(branch) for branch in branches]
            return branches
        else:
            branches = []
            return branches


class ProviderUpdateSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    hospital_branch = serializers.SerializerMethodField()
    
    class Meta:
        model = Provider
        fields = [
            "id",
            "npi_data",
            "hospital",
            "first_name",
            "last_name",
            "email",
            "contact_number",
            "provider_status",
            "hospital_branch",
            "taxonomy_description",
            "taxonomy_code_set",
            "taxonomy_code",
        ]

    def get_email(self, obj):
        return obj.user.email

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name
            
    def get_hospital_branch(self, obj):
        try:
            hospital_branches = obj.hospital_branch_provider.all()
            hospital_branch_list = [model_to_dict(hospital_branch) for hospital_branch in hospital_branches]
        except:
            hospital_branch_list = []
        return hospital_branch_list    


class ProviderAssignedPatientSerializer(serializers.ModelSerializer):
    assigned_patient = serializers.SerializerMethodField()

    class Meta:
        model = Provider
        fields = ["assigned_patient"]

    def get_assigned_patient(self, obj):
        result = "No patient Assigned"
        try:
            primary_provider = PatientProviderMapping.objects.filter(primary_provider=obj)
            provider_patient_list = []
            for provider_patient in primary_provider:
                provider_patient_list.append(provider_patient.patient.pk)
            patient_objs = Patient.objects.filter(id__in=provider_patient_list)
            data = [{
                'id': patient.id,
                'patient_name': patient.user.first_name + " " + patient.user.last_name,
                'provider_name': str(obj),
                'care_manager_name':patient.caremanager.user.first_name + " " + patient.caremanager.user.last_name,
            } for patient in patient_objs]
            return data

        except Exception as e:
            return result
        
    
    


class ProviderStatsSerializer(serializers.ModelSerializer):
    added_date = serializers.SerializerMethodField()
    on_going_treatments = serializers.SerializerMethodField()
    active_treatments = serializers.SerializerMethodField()
    inactive_treatments = serializers.SerializerMethodField()
    total_treatment_completed = serializers.SerializerMethodField()
    total_patient = serializers.SerializerMethodField()
    active_patient = serializers.SerializerMethodField()
    inactive_patient = serializers.SerializerMethodField()
    total_working_hours = serializers.SerializerMethodField()

    class Meta:
        model = Provider
        fields = ["added_date", "on_going_treatments", "active_treatments",
                  "inactive_treatments", "total_treatment_completed", "total_patient",
                  "active_patient", "inactive_patient", "total_working_hours"]

    def get_added_date(self, obj):
        return obj.created_at

    def get_on_going_treatments(self, obj):
        return 0

    def get_active_treatments(self, obj):
        return 0

    def get_inactive_treatments(self, obj):
        return 0

    def get_total_treatment_completed(self, obj):
        return 0

    def get_total_working_hours(self, obj):
        return 0

    def get_inactive_patient(self, obj):
        result = 0
        try:
            primary_provider = PatientProviderMapping.objects.filter(primary_provider=obj)
            ppm_pt_list = []
            for ppm in primary_provider:
                ppm_pt_list.append(ppm.patient.pk)
            patient_objs = Patient.objects.filter(id__in=ppm_pt_list, patient_status="INACTIVE")
            return patient_objs.count()
        except Exception as e:
            return result

    def get_active_patient(self, obj):
        result = 0
        try:
            primary_provider = PatientProviderMapping.objects.filter(primary_provider=obj)
            ppm_pt_list = []
            for ppm in primary_provider:
                ppm_pt_list.append(ppm.patient.pk)
            patient_objs = Patient.objects.filter(id__in=ppm_pt_list, patient_status="ACTIVE")
            return patient_objs.count()
        except Exception as e:
            return result

    def get_total_patient(self, obj):
        result = 0
        try:
            primary_provider = PatientProviderMapping.objects.filter(primary_provider=obj)
            ppm_pt_list = []
            for ppm in primary_provider:
                ppm_pt_list.append(ppm.patient.pk)
            patient_objs = Patient.objects.filter(id__in=ppm_pt_list)
            return patient_objs.count()
        except Exception as e:
            return result


class CommunicationSerializers(serializers.ModelSerializer):
    class Meta:
        model = Communication
        fields = "__all__"


class PatientProviderMappingSerializer(serializers.ModelSerializer):
    patient = PatientSerializer()
    primary_provider = ProviderSerializer()
    secondary_provider = ProviderSerializer()

    class Meta:
        model = PatientProviderMapping
        fields = ["patient", "primary_provider", "secondary_provider"]


class PatientProviderMappingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProviderMapping
        fields = ["patient", "primary_provider", "secondary_provider"]


class ProvidersPatientListSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    risk_score = serializers.SerializerMethodField()
    review_date = serializers.SerializerMethodField()
    joining_date = serializers.SerializerMethodField()
    provider_assigned = serializers.SerializerMethodField()
    minutes_completed = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ["patient_name", "risk_score", "review_date", "joining_date", "provider_assigned", "minutes_completed"]

    def get_patient_name(self, obj):
        return f"{obj.user.get_full_name()}"

    def get_risk_score(self, obj):
        return 10

    def get_review_date(self, obj):
        return 10

    def get_joining_date(self, obj):
        return obj.user.created_at

    def get_provider_assigned(self, obj):
        ppm = PatientProviderMapping.objects.filter(patient=obj).last()
        return ppm.primary_provider.user.get_full_name()

    def get_minutes_completed(self, obj):
        return 10


class CareManagerProviderSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    no_of_patients = serializers.SerializerMethodField()
    minutes_completed = serializers.SerializerMethodField()

    class Meta:
        model = Provider
        fields = [
            "id",
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "full_name",
            "gender",
            "npi_data",
            "contact_number",
            "taxonomy_description",
            "taxonomy_code_set",
            "taxonomy_code",
            "address_1",
            "address_2",
            "city",
            "state",
            "zip_code",
            "profile_pic",
            "created_at",
            "provider_status",
            "department",
            "no_of_patients",
            "minutes_completed",
            "contact_number_two"
            
        ]

    def get_email(self, obj):
        return obj.user.email

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    def get_profile_pic(self, obj):
        try:
            if obj.user.profile_pic:
                return settings.BACKEND_URL + obj.user.profile_pic.url
            else:
                return None
        except:
            return None

    def get_department(self, obj):
        return None

    def get_no_of_patients(self, obj):
        return PatientProviderMapping.objects.filter(primary_provider=obj).count()

    def get_minutes_completed(self, obj):
        return 10


class PatientListForCareManagerSerializer(serializers.Serializer):
    patient_name = serializers.SerializerMethodField()
    risk_score = serializers.SerializerMethodField()
    review_date = serializers.SerializerMethodField()
    enrolled_date = serializers.SerializerMethodField()
    provider_assigned = serializers.SerializerMethodField()
    condition1 = serializers.SerializerMethodField()
    condition2 = serializers.SerializerMethodField()
    minutes_completed = serializers.SerializerMethodField()
    patient_id = serializers.SerializerMethodField()
    patient_profile_pic = serializers.SerializerMethodField()
    caremanager = serializers.SerializerMethodField()
    cell_phone = serializers.SerializerMethodField()
    dob = serializers.SerializerMethodField()
    chronic_disease = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()


    class Meta:
        model = Patient
        fields = ["patient_id", "dob", "patient_name", "risk_score", "review_date", "enrolled_date", "provider_assigned",
                  "condition1", "condition2", "minutes_completed", "patient_profile_pic","caremanager", "cell_phone", "chronic_disease"]

    def get_chronic_disease(self, obj):
        chronic_name = PatientChronicDisease.objects.filter(patient=obj).values_list('chronic__disease_name', flat=True)
        return chronic_name

    def get_patient_profile_pic(self, obj):
        if obj.user.profile_pic:
            return settings.BACKEND_URL + obj.user.profile_pic.url
        else:
            return None

    def get_patient_id(self, obj):
        return obj.id
    
    def get_gender(self, obj):
        return obj.gender

    def get_dob(self, obj):
        return obj.dob

    def get_caremanager(self, obj):
        if obj.caremanager_obj:
            return get_user_full_name(obj.caremanager_obj.user)
        else:
            return None

    def get_patient_name(self, obj):
        return obj.user.get_full_name()

    def get_risk_score(self, obj):
        return 10

    def get_review_date(self, obj):
        return str(obj.created_at)

    def get_enrolled_date(self, obj):
        return str(obj.created_at)

    def get_provider_assigned(self, obj):
        ppm = PatientProviderMapping.objects.filter(patient=obj).last()
        if ppm:
            if ppm.primary_provider:
                return ppm.primary_provider.user.get_full_name()
            else:
                return None
        else:
            return None
        # ppm = PatientProviderMapping.objects.filter(patient=obj)
        # if ppm:
        #     return True
        # else:
        #     return False

    def get_condition1(self, obj):
        return None
        # ppm = PatientProviderMapping.objects.filter(patient=obj).last()
        # if ppm:
        #     if ppm.primary_provider:
        #         return ppm.primary_provider.user.get_full_name()
        #     else:
        #         return None
        # else:
        # return None

    def get_condition2(self, obj):
        return None
        # ppm = PatientProviderMapping.objects.filter(patient=obj).last()
        # if ppm:
        #     if ppm.secondary_provider:
        #         return ppm.secondary_provider.user.get_full_name()

        #     else:
        #         return None
        # else:
        # return None
    
    def get_minutes_completed(self, obj):
        result_sum = 0
        try:
            vcall = VitalCallLog.objects.filter(patient=obj)
            mcall = MedicalConditionCallLog.objects.filter(patient=obj)
            acall = AssessmentCallLog.objects.filter(patient=obj)
            awvcall = AnnualWellnessVisitCallLog.objects.filter(patient=obj)
            smpcall = SelfManagementPlanCallLog.objects.filter(patient=obj)

            total_vcall_duration = sum([i.call_duration.seconds for i in vcall])
            total_mcall_duration = sum([i.call_duration.seconds for i in mcall])
            total_acall_duration = sum([i.call_duration.seconds  for i in acall])
            total_awvcall_duration = sum([i.call_duration.seconds for i in awvcall])
            total_smpcall_duration = sum([i.call_duration.seconds for i in smpcall])
            total_call_duration = total_vcall_duration + total_mcall_duration + total_acall_duration + total_awvcall_duration + total_smpcall_duration
            time = strftime("%H:%M:%S", gmtime(total_call_duration))
            total_call_duration_in_hours_minutes = ":".join(time.split(":")[:2])
            return total_call_duration_in_hours_minutes

        except Exception as e:
            return result_sum
        
    def get_cell_phone(self, obj):
        if obj.patient_contact_detail:
            cell_phone = obj.patient_contact_detail.all()
            for number in cell_phone:
                return number.cell_phone
        else: 
            return None    
            


class CaremanagerPatientProfileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    provider_name = serializers.SerializerMethodField()
    contact_number = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ["id", "name", "age", "gender", "provider_name", "contact_number", "profile_pic", "dob"]

    def get_name(self, obj):
        name = None
        if obj.user:
            name = obj.user.get_full_name()
        return name

    def get_age(self, obj):
        age = None
        if obj.dob:
            today = date.today()
            age = today.year - obj.dob.year - ((today.month, today.day) < (obj.dob.month, obj.dob.day))
        return age

    def get_provider_name(self, obj):
        for patient_provider in obj.patient_patientprovidermapping.all():
            if patient_provider.primary_provider:
                provider = patient_provider.primary_provider.user.get_full_name()
                return provider
            else:
                return None
        else:
            return None

    def get_contact_number(self, obj):
        pcd = PatientContactDetails.objects.filter(patient=obj).last()
        if pcd:
            return pcd.cell_phone
        else:
            return None

    def get_profile_pic(self, obj):
        if obj.user.profile_pic:
            return settings.BACKEND_URL + obj.user.profile_pic.url
        else:
            return None
    
 


# class CaremanagerTaskListSerializer(serializers.ModelSerializer):
#     todays_tasks = serializers.SerializerMethodField()
#     completed_tasks = serializers.SerializerMethodField()
#     overdue_tasks = serializers.SerializerMethodField()
#     tomorrow_tasks = serializers.SerializerMethodField()
#     next_week_tasks = serializers.SerializerMethodField()

#     class Meta:
#         model = Task
#         fields = ['todays_tasks', 'completed_tasks', 'overdue_tasks', 'tomorrow_tasks', 'next_week_tasks']

#     def get_todays_tasks(self, obj):
#         result = []
#         try:
#             today = datetime.datetime.now().date()
#             tasks = Task.objects.filter(care_manager=obj, task_date=today)
#             goals = Goal.objects.filter(goal_date__date=today)
#             outreaches = PatientOutreach.objects.filter(schedule_follow_up_date=today)
#             combined_queryset = list(chain(tasks, goals, outreaches))
#             print(combined_queryset)
#             result = build_task_data(combined_queryset)
#             return result
#         except Exception as e:
#             print(e)
#             return result

#     def get_completed_tasks(self, obj):
#         result = {}
#         try:
#             tasks = Task.objects.filter(care_manager=obj, task_status="COMPLETED")
#             goals = Goal.objects.filter(goal_status="COMPLETED")
#             outreaches = PatientOutreach.objects.filter(outreach_status="COMPLETED")
#             combined_queryset = list(chain(tasks, goals, outreaches))
#             print(combined_queryset)
#             result = build_task_data(combined_queryset)
#             return result
#         except Exception as e:
#             return result

#     def get_overdue_tasks(self, obj):
#         result = {}
#         try:
#             today = datetime.datetime.now().date()
#             tasks = Task.objects.filter(care_manager=obj, task_date__lt=today)
#             goals = Goal.objects.filter(goal_date__date__lt=today)
#             outreaches = PatientOutreach.objects.filter(schedule_follow_up_date__lt=today)
#             combined_queryset = list(chain(tasks, goals, outreaches))
#             print(combined_queryset)
#             result = build_task_data(combined_queryset)
#             return result
#         except Exception as e:
#             return result

#     def get_tomorrow_tasks(self, obj):
#         result = {}
#         try:
#             today = datetime.datetime.now().date()
#             tomorrow = today + datetime.timedelta(1)
#             tasks = Task.objects.filter(care_manager=obj, task_date=tomorrow)
#             goals = Goal.objects.filter(goal_date__date=tomorrow)
#             outreaches = PatientOutreach.objects.filter(schedule_follow_up_date=tomorrow)
#             combined_queryset = list(chain(tasks, goals, outreaches))
#             print(combined_queryset)
#             result = build_task_data(combined_queryset)
#             return result
#         except Exception as e:
#             return result

#     def get_next_week_tasks(self, obj):
#         result = {}
#         try:
#             today = datetime.datetime.now().date()
#             next_week = today + datetime.timedelta(7)
#             tasks = Task.objects.filter(care_manager=obj, task_date__range=[today, next_week])
#             goals = Goal.objects.filter(goal_date__date__range=[today, next_week])
#             outreaches = PatientOutreach.objects.filter(schedule_follow_up_date__range=[today, next_week])
#             combined_queryset = list(chain(tasks, goals, outreaches))
#             print(combined_queryset)
#             result = build_task_data(combined_queryset)
#             return result
#         except Exception as e:
#             return result


class PatientProSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id']


class MultiplePatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProviderMapping
        fields = ['primary_provider', 'patient']


class ChronicPatientCountSerializer(serializers.ModelSerializer):
    chronic_patient_count = serializers.SerializerMethodField()

    class Meta:
        model = PatientChronicDisease
        fields = ["chronic_patient_count"]

    def get_chronic_patient_count(self, obj):
        result = 0
        try:
            chronic_condition = ChronicCondition.objects.all()
            chronic_patient_id_list = []
            chronic_name_list = []
            chronic_count = []
            for chronic in chronic_condition:
                chronic_patient_id_list.append(chronic.id)
                chronic_name_list.append(chronic.disease_name)
            for chronic in chronic_patient_id_list:
                patient_objs = PatientChronicDisease.objects.filter(chronic=chronic)
                chronic_count.append(patient_objs.count())
            res = dict(zip(chronic_name_list, chronic_count))
            return res

        except Exception as e:
            return result


class PatientStatsTotalPatientSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Patient
        fields = ['pk', 'user']


class CareManagerPatientSerializer(serializers.ModelSerializer):
    patient = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ['patient']

    def get_patient(self, obj, format=None):
        result = []
        patients = self.context['data']
        zero_to_ten = self.context['zero_to_ten']
        ten_to_twenty = self.context['ten_to_twenty']
        above_twenty = self.context['above_twenty']

        try:
            for patient in patients:
                vcall = VitalCallLog.objects.filter(patient=patient, care_manager=obj)
                mcall = MedicalConditionCallLog.objects.filter(patient=patient, care_manager=obj)
                acall = AssessmentCallLog.objects.filter(patient=patient, care_manager=obj)
                awvcall = AnnualWellnessVisitCallLog.objects.filter(patient=patient, care_manager=obj)
                smpcall = SelfManagementPlanCallLog.objects.filter(patient=patient, care_manager=obj)
                pcall = PatientCallLog.objects.filter(patient=patient, care_manager=obj)

                total_vcall_duration = sum([i.call_duration.seconds//60 for i in vcall if i.call_duration])
                total_mcall_duration = sum([i.call_duration.seconds//60 for i in mcall if i.call_duration])
                total_acall_duration = sum([i.call_duration.seconds//60 for i in acall if i.call_duration])
                total_awvcall_duration = sum([i.call_duration.seconds//60 for i in awvcall if i.call_duration])
                total_smpcall_duration = sum([i.call_duration.seconds//60 for i in smpcall if i.call_duration])
                total_pcall_duration = sum([ i.call_duration.seconds//60 for i in pcall if i.call_duration])
                total_call_duration = total_vcall_duration + total_mcall_duration + total_acall_duration + total_awvcall_duration + total_smpcall_duration
                + total_pcall_duration

                if zero_to_ten == '0-10' and total_call_duration >= 0 and total_call_duration <= 10:
                    ppm = PatientProviderMapping.objects.filter(patient=patient).last()
                    if ppm:
                        if ppm.primary_provider:
                            provider_assigned = ppm.primary_provider.user.get_full_name()
                    else:
                        provider_assigned = ''
                    data = {}
                    data['patient_id'] = patient.id
                    data['patient_name'] = patient.user.get_full_name()
                    data['risk_score'] = 10
                    data['review_date'] = str(patient.created_at)
                    data['enrolled_date'] = str(patient.created_at)
                    data['provider_assigned'] = provider_assigned
                    data['condition1'] = None
                    data['condition2'] = None
                    data['minutes_completed'] = total_call_duration
                    data['caremanager'] = patient.caremanager_obj.user.get_full_name()
                    data['cell_phone'] = patient.patient_contact_detail.values_list('cell_phone',flat=True).first()
                    result.append(data)
                elif ten_to_twenty == '10-20' and total_call_duration >= 11 and total_call_duration < 20:
                    ppm = PatientProviderMapping.objects.filter(patient=patient).last()
                    if ppm:
                        if ppm.primary_provider:
                            provider_assigned = ppm.primary_provider.user.get_full_name()
                    else:
                        provider_assigned = ''
                    data = {}
                    data['patient_id'] = patient.id
                    data['patient_name'] = patient.user.get_full_name()
                    data['risk_score'] = 10
                    data['review_date'] = str(patient.created_at)
                    data['enrolled_date'] = str(patient.created_at)
                    data['provider_assigned'] = provider_assigned
                    data['condition1'] = None
                    data['condition2'] = None
                    data['minutes_completed'] = total_call_duration
                    data['caremanager'] = patient.caremanager_obj.user.get_full_name()
                    data['cell_phone'] = patient.patient_contact_detail.values_list('cell_phone',flat=True).first()
                    result.append(data)
                elif above_twenty == '20' and total_call_duration >= 20:
                    ppm = PatientProviderMapping.objects.filter(patient=patient).last()
                    if ppm:
                        if ppm.primary_provider:
                            provider_assigned = ppm.primary_provider.user.get_full_name()
                    else:
                        provider_assigned = ''
                    data = {}
                    data['patient_id'] = patient.id
                    data['patient_name'] = patient.user.get_full_name()
                    data['risk_score'] = 10
                    data['review_date'] = str(patient.created_at)
                    data['enrolled_date'] = str(patient.created_at)
                    data['provider_assigned'] = provider_assigned
                    data['condition1'] = None
                    data['condition2'] = None
                    data['minutes_completed'] = total_call_duration
                    data['caremanager'] = patient.caremanager_obj.user.get_full_name()
                    data['cell_phone'] = patient.patient_contact_detail.values_list('cell_phone',flat=True).first()
                    result.append(data)

            return result
        except Exception as e:
            return None


class CaremanagerPatientCountSerializer(serializers.ModelSerializer):
    care_manager = serializers.SerializerMethodField()
    class Meta:
        model = CareManager
        fields = ['care_manager']

    def get_care_manager(self, caremanagers):
        data = {}
        for cm in caremanagers:
            patient_count = cm.patient_care_manager.all().count()
            data[cm.user.get_full_name()] = patient_count
        caremanager_patients = dict(sorted(data.items(), key=lambda x: (-x[1], x[0]))[:5])
        return caremanager_patients


class ProviderPatientCountSerializer(serializers.ModelSerializer):
    provider = serializers.SerializerMethodField()

    class Meta:
        model = Provider
        fields = ['provider']

    def get_provider(self, providers):
        data = {}
        for provider in providers:
            data[provider.user.get_full_name()] = provider.pri_provider.all().count()
        provider_patients = dict(sorted(data.items(), key=lambda x: (-x[1], x[0]))[:5])
        return provider_patients


class ChronicConditionPatientCountSerializer(serializers.ModelSerializer):
    chronic = serializers.SerializerMethodField()

    class Meta:
        model = ChronicCondition
        fields = ['chronic']

    def get_chronic(self, chronics):
        data = {}
        for chronic in chronics:
            data[chronic.disease_name] = chronic.chronic_disease.all().count()
        chronic_patients = dict(sorted(data.items(), key=lambda x: (-x[1], x[0]))[:5])
        return chronic_patients


class CaremanagerTaskOutreachListSerializer(serializers.Serializer):
    todays_tasks = serializers.SerializerMethodField()
    completed_tasks = serializers.SerializerMethodField()
    overdue_tasks = serializers.SerializerMethodField()
    tomorrow_tasks = serializers.SerializerMethodField()
    next_week_tasks = serializers.SerializerMethodField()

    class Meta:
        # model = Task
        fields = ['todays_tasks', 'completed_tasks', 'overdue_tasks', 'tomorrow_tasks', 'next_week_tasks']

    def get_todays_tasks(self, obj):
        result = []
        try:
            today = datetime.datetime.now().date()
            request = self.context["request"]
            tasks = Task.objects.filter(care_manager=obj, task_date=today)
            outreaches = PatientOutreach.objects.filter(care_manager=obj, schedule_follow_up_date=today)
            cm_notes = CareManagerNotes.objects.filter(care_manager=obj, caremanager_notes_date=today)
            task_name = request.query_params.get('task_name')            
            patient_name = request.query_params.get('patient_name')
            task_type = request.query_params.get('task_type')
            from_date = request.query_params.get('from_date',None)
            to_date = request.query_params.get('to_date',None)
            
            if patient_name:
                tasks = Task.objects.annotate(full_name=Concat('patient__user__first_name', Value(' '), 'patient__user__last_name')).filter(Q(full_name__iexact=patient_name) | Q(patient__user__first_name__icontains=patient_name) | Q(patient__user__last_name__icontains=patient_name),care_manager=obj)
                outreaches = PatientOutreach.objects.annotate(full_name=Concat('patient__user__first_name', Value(' '), 'patient__user__last_name')).filter(Q(full_name__iexact=patient_name) | Q(patient__user__first_name__icontains=patient_name) | Q(patient__user__last_name__icontains=patient_name),care_manager=obj)
                cm_notes = CareManagerNotes.objects.annotate(full_name=Concat('patient__user__first_name', Value(' '), 'patient__user__last_name')).filter(Q(full_name__iexact=patient_name) | Q(patient__user__first_name__icontains=patient_name) | Q(patient__user__last_name__icontains=patient_name),care_manager=obj)
                # name = patient_name.split()
                # if len(name) > 1:
                #     first_name = patient_name.split()[0]
                #     last_name = patient_name.split()[1]
                #     tasks = Task.objects.filter(care_manager=obj, patient__user__first_name__iexact=first_name, patient__user__last_name__iexact=last_name)
                #     outreaches = PatientOutreach.objects.filter(care_manager=obj, patient__user__first_name=first_name, patient__user__last_name=last_name)
                #     cm_notes = CareManagerNotes.objects.filter(care_manager=obj, patient__user__first_name=first_name, patient__user__last_name=last_name)
                # else:
                #     tasks = Task.objects.filter(care_manager=obj, patient__user__first_name__icontains=patient_name)
                #     outreaches = PatientOutreach.objects.filter(care_manager=obj, patient__user__first_name__icontains=patient_name)
                #     cm_notes = CareManagerNotes.objects.filter(care_manager=obj, patient__user__first_name__icontains=patient_name)
            if task_name:
                tasks = Task.objects.filter(care_manager=obj, name__icontains=task_name)
                outreaches = PatientOutreach.objects.filter(care_manager=obj, notes__icontains=task_name)  
                cm_notes = CareManagerNotes.objects.filter(care_manager=obj, notes__icontains=task_name)
            if from_date and to_date:
                tasks = Task.objects.filter(care_manager=obj, task_date=today, modified_at__date__range=[from_date, to_date])
                outreaches = PatientOutreach.objects.filter(care_manager=obj, schedule_follow_up_date=today, modified_at__date__range=[from_date, to_date])
                cm_notes = CareManagerNotes.objects.filter(care_manager=obj, caremanager_notes_date=today, modified_at__date__range=[from_date, to_date])
            if task_type == "Task":
                combined_queryset = list(chain(tasks))
            elif task_type == "Intervention":
                combined_queryset = list(chain(outreaches))
            elif task_type == "Notes":
                combined_queryset = list(chain(cm_notes))     
            else:
                combined_queryset = list(chain(tasks, outreaches, cm_notes))      
            result = build_task_data(combined_queryset)
            return result
        except Exception as e:
            print(e)
            return result

    def get_completed_tasks(self, obj):
        result = {}
        try:
            request = self.context["request"]
            tasks = Task.objects.filter(care_manager=obj, task_status="COMPLETED")
            outreaches = PatientOutreach.objects.filter(care_manager=obj,outreach_status="COMPLETED")
            cm_notes = CareManagerNotes.objects.filter(care_manager=obj, cm_notes_status="COMPLETED")
            task_name = request.query_params.get('task_name')            
            patient_name = request.query_params.get('patient_name')
            task_type = request.query_params.get('task_type')
            from_date = request.query_params.get('from_date',None)
            to_date = request.query_params.get('to_date',None)
                        
            if patient_name:
                tasks = Task.objects.annotate(full_name=Concat('patient__user__first_name', Value(' '), 'patient__user__last_name')).filter(Q(full_name__iexact=patient_name) | Q(patient__user__first_name__icontains=patient_name) | Q(patient__user__last_name__icontains=patient_name),care_manager=obj, task_status="COMPLETED")
                outreaches = PatientOutreach.objects.annotate(full_name=Concat('patient__user__first_name', Value(' '), 'patient__user__last_name')).filter(Q(full_name__iexact=patient_name) | Q(patient__user__first_name__icontains=patient_name) | Q(patient__user__last_name__icontains=patient_name),care_manager=obj, outreach_status="COMPLETED")
                cm_notes = CareManagerNotes.objects.annotate(full_name=Concat('patient__user__first_name', Value(' '), 'patient__user__last_name')).filter(Q(full_name__iexact=patient_name) | Q(patient__user__first_name__icontains=patient_name) | Q(patient__user__last_name__icontains=patient_name),care_manager=obj, cm_notes_status="COMPLETED")
                # tasks = Task.objects.filter(care_manager=obj, patient__user__first_name__icontains=patient_name, task_status="COMPLETED")
                # outreaches = PatientOutreach.objects.filter(care_manager=obj, outreach_status="COMPLETED", patient__user__first_name__icontains=patient_name)
                # cm_notes = CareManagerNotes.objects.filter(care_manager=obj, cm_notes_status="COMPLETED", patient__user__first_name__icontains=patient_name)
                
            if task_name:
                tasks = Task.objects.filter(care_manager=obj, name__icontains=task_name, task_status="COMPLETED")
                outreaches = PatientOutreach.objects.filter(care_manager=obj, outreach_status="COMPLETED", notes__icontains=task_name)
                cm_notes = CareManagerNotes.objects.filter(care_manager=obj, cm_notes_status="COMPLETED", notes__icontains=task_name)
                   
            if from_date and to_date:
                tasks = Task.objects.filter(care_manager=obj, task_status="COMPLETED", modified_at__date__range=[from_date, to_date] )
                outreaches = PatientOutreach.objects.filter(care_manager=obj,outreach_status="COMPLETED", modified_at__date__range=[from_date, to_date])
                cm_notes = CareManagerNotes.objects.filter(care_manager=obj, cm_notes_status="COMPLETED", modified_at__date__range=[from_date, to_date])
                 
            if task_type == "Task":
                combined_queryset = list(chain(tasks))
            elif task_type == "Intervention":
                combined_queryset = list(chain(outreaches)) 
            elif task_type == "Notes":
                combined_queryset = list(chain(cm_notes))     
            else:
                combined_queryset = list(chain(tasks, outreaches, cm_notes))  
            result = build_task_data(combined_queryset)
            return result
        except Exception as e:
            return result

    def get_overdue_tasks(self, obj):
        result = {}
        try:
            request = self.context["request"]
            today = datetime.datetime.now().date()
            tasks = Task.objects.filter(care_manager=obj, task_date__lt=today)
            outreaches = PatientOutreach.objects.filter(care_manager=obj, schedule_follow_up_date__lt=today)
            cm_notes = CareManagerNotes.objects.filter(care_manager=obj, caremanager_notes_date__lt=today)
            
            task_name = request.query_params.get('task_name')            
            patient_name = request.query_params.get('patient_name')
            task_type = request.query_params.get('task_type')
            from_date = request.query_params.get('from_date',None)
            to_date = request.query_params.get('to_date',None)
            
            if patient_name:
                tasks = Task.objects.annotate(full_name=Concat('patient__user__first_name', Value(' '), 'patient__user__last_name')).filter(Q(full_name__iexact=patient_name) | Q(patient__user__first_name__icontains=patient_name) | Q(patient__user__last_name__icontains=patient_name),care_manager=obj, task_date__lt=today)
                outreaches = PatientOutreach.objects.annotate(full_name=Concat('patient__user__first_name', Value(' '), 'patient__user__last_name')).filter(Q(full_name__iexact=patient_name) | Q(patient__user__first_name__icontains=patient_name) | Q(patient__user__last_name__icontains=patient_name),care_manager=obj, schedule_follow_up_date__lt=today)
                cm_notes = CareManagerNotes.objects.annotate(full_name=Concat('patient__user__first_name', Value(' '), 'patient__user__last_name')).filter(Q(full_name__iexact=patient_name) | Q(patient__user__first_name__icontains=patient_name) | Q(patient__user__last_name__icontains=patient_name),care_manager=obj, caremanager_notes_date__lt=today)
                # tasks = Task.objects.filter(care_manager=obj, patient__user__first_name__icontains=patient_name, task_date__lt=today)
                # outreaches = PatientOutreach.objects.filter(care_manager=obj, schedule_follow_up_date__lt=today, patient__user__first_name__icontains=patient_name)
                # cm_notes = CareManagerNotes.objects.filter(care_manager=obj, caremanager_notes_date__lt=today,  patient__user__first_name__icontains=patient_name)
                
            if task_name:
                tasks = Task.objects.filter(care_manager=obj, name__icontains=task_name, task_date__lt=today)
                outreaches = PatientOutreach.objects.filter(care_manager=obj, schedule_follow_up_date__lt=today, notes__icontains=task_name)    
                cm_notes = CareManagerNotes.objects.filter(care_manager=obj, caremanager_notes_date__lt=today, notes__icontains=task_name)

            if from_date and to_date:
                tasks = Task.objects.filter(care_manager=obj, task_date__lt=today, modified_at__date__range=[from_date, to_date] )
                outreaches = PatientOutreach.objects.filter(care_manager=obj, schedule_follow_up_date__lt=today, modified_at__date__range=[from_date, to_date])
                cm_notes = CareManagerNotes.objects.filter(care_manager=obj, caremanager_notes_date__lt=today, modified_at__date__range=[from_date, to_date])

            if task_type == "Task":
                combined_queryset = list(chain(tasks))
            elif task_type == "Intervention":
                combined_queryset = list(chain(outreaches)) 
            elif task_type == "Notes":
                combined_queryset = list(chain(cm_notes))     
            else:
                combined_queryset = list(chain(tasks, outreaches, cm_notes))
            print(combined_queryset)
            result = build_task_data(combined_queryset)
            return result
        except Exception as e:
            return result

    def get_tomorrow_tasks(self, obj):
        result = {}
        try:
            request = self.context["request"]
            today = datetime.datetime.now().date()
            tomorrow = today + datetime.timedelta(1)
            tasks = Task.objects.filter(care_manager=obj, task_date=tomorrow)
            outreaches = PatientOutreach.objects.filter(care_manager=obj,schedule_follow_up_date=tomorrow)
            cm_notes = CareManagerNotes.objects.filter(care_manager=obj, caremanager_notes_date=tomorrow)
            
            task_name = request.query_params.get('task_name')            
            patient_name = request.query_params.get('patient_name')
            task_type = request.query_params.get('task_type')
            from_date = request.query_params.get('from_date',None)
            to_date = request.query_params.get('to_date',None)
                        
            if patient_name:
                tasks = Task.objects.annotate(full_name=Concat('patient__user__first_name', Value(' '), 'patient__user__last_name')).filter(Q(full_name__iexact=patient_name) | Q(patient__user__first_name__icontains=patient_name) | Q(patient__user__last_name__icontains=patient_name),care_manager=obj, task_date=tomorrow)
                outreaches = PatientOutreach.objects.annotate(full_name=Concat('patient__user__first_name', Value(' '), 'patient__user__last_name')).filter(Q(full_name__iexact=patient_name) | Q(patient__user__first_name__icontains=patient_name) | Q(patient__user__last_name__icontains=patient_name),care_manager=obj, schedule_follow_up_date=tomorrow)
                cm_notes = CareManagerNotes.objects.annotate(full_name=Concat('patient__user__first_name', Value(' '), 'patient__user__last_name')).filter(Q(full_name__iexact=patient_name) | Q(patient__user__first_name__icontains=patient_name) | Q(patient__user__last_name__icontains=patient_name),care_manager=obj, caremanager_notes_date=tomorrow)
                # tasks = Task.objects.filter(care_manager=obj, patient__user__first_name__icontains=patient_name, task_date=tomorrow)
                # outreaches = PatientOutreach.objects.filter(care_manager=obj, schedule_follow_up_date=tomorrow, patient__user__first_name__icontains=patient_name)
                # cm_notes = CareManagerNotes.objects.filter(care_manager=obj, caremanager_notes_date=tomorrow, patient__user__first_name__icontains=patient_name)
                
            if task_name:
                tasks = Task.objects.filter(care_manager=obj, name__icontains=task_name, task_date=tomorrow)
                outreaches = PatientOutreach.objects.filter(care_manager=obj, schedule_follow_up_date=tomorrow, notes__icontains=task_name)  
                cm_notes = CareManagerNotes.objects.filter(care_manager=obj, caremanager_notes_date=tomorrow, notes__icontains=task_name)

            if from_date and to_date:
                tasks = Task.objects.filter(care_manager=obj, task_date=tomorrow, modified_at__date__range=[from_date, to_date] )
                outreaches = PatientOutreach.objects.filter(care_manager=obj,schedule_follow_up_date=tomorrow, modified_at__date__range=[from_date, to_date])
                cm_notes = CareManagerNotes.objects.filter(care_manager=obj, caremanager_notes_date=tomorrow, modified_at__date__range=[from_date, to_date])

            if task_type == "Task":
                combined_queryset = list(chain(tasks))
            elif task_type == "Intervention":
                combined_queryset = list(chain(outreaches)) 
            elif task_type == "Notes":
                combined_queryset = list(chain(cm_notes))     
            else:
                combined_queryset = list(chain(tasks, outreaches, cm_notes))
            print(combined_queryset)
            result = build_task_data(combined_queryset)
            return result
        except Exception as e:
            return result

    def get_next_week_tasks(self, obj):
        result = {}
        try:
            request = self.context["request"]
            today = datetime.datetime.now().date()
            next_week = today + datetime.timedelta(7)
            tasks = Task.objects.filter(care_manager=obj, task_date__range=[today, next_week])
            outreaches = PatientOutreach.objects.filter(care_manager=obj, schedule_follow_up_date__range=[today, next_week])
            cm_notes = CareManagerNotes.objects.filter(care_manager=obj, caremanager_notes_date__range=[today, next_week])
            
            task_name = request.query_params.get('task_name')            
            patient_name = request.query_params.get('patient_name')
            task_type = request.query_params.get('task_type')
            from_date = request.query_params.get('from_date',None)
            to_date = request.query_params.get('to_date',None)
                        
            if patient_name:
                tasks = Task.objects.annotate(full_name=Concat('patient__user__first_name', Value(' '), 'patient__user__last_name')).filter(Q(full_name__iexact=patient_name) | Q(patient__user__first_name__icontains=patient_name) | Q(patient__user__last_name__icontains=patient_name),care_manager=obj, task_date__range=[today, next_week])
                outreaches = PatientOutreach.objects.annotate(full_name=Concat('patient__user__first_name', Value(' '), 'patient__user__last_name')).filter(Q(full_name__iexact=patient_name) | Q(patient__user__first_name__icontains=patient_name) | Q(patient__user__last_name__icontains=patient_name),care_manager=obj, schedule_follow_up_date__range=[today, next_week])
                cm_notes = CareManagerNotes.objects.annotate(full_name=Concat('patient__user__first_name', Value(' '), 'patient__user__last_name')).filter(Q(full_name__iexact=patient_name) | Q(patient__user__first_name__icontains=patient_name) | Q(patient__user__last_name__icontains=patient_name),care_manager=obj, caremanager_notes_date__range=[today, next_week])
                # tasks = Task.objects.filter(care_manager=obj, patient__user__first_name__icontains=patient_name, task_date__range=[today, next_week])
                # outreaches = PatientOutreach.objects.filter(care_manager=obj, schedule_follow_up_date__range=[today, next_week], patient__user__first_name__icontains=patient_name)
                # cm_notes = CareManagerNotes.objects.filter(care_manager=obj, caremanager_notes_date__range=[today, next_week], patient__user__first_name__icontains=patient_name)

            if task_name:
                tasks = Task.objects.filter(care_manager=obj, name__icontains=task_name, task_date__range=[today, next_week])
                outreaches = PatientOutreach.objects.filter(care_manager=obj, schedule_follow_up_date__range=[today, next_week], notes__icontains=task_name)    
                cm_notes = CareManagerNotes.objects.filter(care_manager=obj, caremanager_notes_date__range=[today, next_week], notes__icontains=task_name)
    
            if from_date and to_date:
                tasks = Task.objects.filter(care_manager=obj, task_date__range=[today, next_week], modified_at__date__range=[from_date, to_date] )
                outreaches = PatientOutreach.objects.filter(care_manager=obj, schedule_follow_up_date__range=[today, next_week], modified_at__date__range=[from_date, to_date])
                cm_notes = CareManagerNotes.objects.filter(care_manager=obj, caremanager_notes_date__range=[today, next_week], modified_at__date__range=[from_date, to_date])
                  
            if task_type == "Task":
                combined_queryset = list(chain(tasks))
            elif task_type == "Intervention":
                combined_queryset = list(chain(outreaches)) 
            elif task_type == "Notes":
                combined_queryset = list(chain(cm_notes))     
            else:
                combined_queryset = list(chain(tasks, outreaches, cm_notes))
            print(combined_queryset)
            result = build_task_data(combined_queryset)
            return result
        except Exception as e:
            return result

class GetCaremanagerPracticeSerializer(serializers.ModelSerializer):
    hospital = serializers.SerializerMethodField()
    class Meta:
        model = CareManager
        fields = ['hospital']
        
    def get_hospital(self, obj):
        try:
            if obj.hospital:
                return obj.hospital.hospital_name
            else:
                return None  
        except:
            return None  
        
        
class GetHospitalCareManagerSerializer(serializers.ModelSerializer):
    caremanager_name = serializers.SerializerMethodField()

    class Meta:
        model = CareManager
        fields = ["id", "caremanager_name"]
    
    def get_caremanager_name(self, obj):
        return obj.user.get_full_name()
    

class GetHospitalCareManagerSerializer(serializers.ModelSerializer):
    caremanager_name = serializers.SerializerMethodField()

    class Meta:
        model = CareManager
        fields = ["id", "caremanager_name"]
    
    def get_caremanager_name(self, obj):
        return obj.user.get_full_name()    
    
    
class GetCareManagerlistSerializer(serializers.ModelSerializer):
    caremanager_name = serializers.SerializerMethodField()
    caremanager_email = serializers.SerializerMethodField()
    caremanager_contact = serializers.SerializerMethodField()
    assigned_patient = serializers.SerializerMethodField()
    previous_month_minutes = serializers.SerializerMethodField()
    current_month_minutes = serializers.SerializerMethodField()    
    
    class Meta:
        model = CareManager
        fields = ["id", "caremanager_name", "caremanager_email", "caremanager_contact",  "assigned_patient", "previous_month_minutes", "current_month_minutes"]
    
    def get_caremanager_name(self, obj):
        return obj.user.get_full_name()   
    
    def get_caremanager_email(self, obj):
        return obj.user.email
    
    def get_caremanager_contact(self, obj):
        return obj.contact
    
    def get_assigned_patient(self, obj):
        assiged_patient = obj.patients_care_manager.all().count()
        return assiged_patient
    
    def get_current_month_minutes(self, obj):
        patient_objs = Patient.objects.filter(caremanager_obj=obj)
        list1 = []
        for obj in patient_objs:
            session_total_time = get_session_total_time_current_month(obj)
            total_time = get_mannual_total_time_current_month(obj)
            total_monthly_time = total_time + session_total_time  
            list1.append(total_monthly_time)
        time_in_hrs_min = ':'.join((str(datetime.timedelta(seconds=sum(list1)))).split(":")[:-1])
        current_month_time_hrs = int(time_in_hrs_min.split(":")[0]) * 60
        current_month_time_min = int(time_in_hrs_min.split(":")[1])
        current_month_time_in_total_min = current_month_time_hrs + current_month_time_min
        return current_month_time_in_total_min
    
    def get_previous_month_minutes(self, obj):
        patient_objs = Patient.objects.filter(caremanager_obj=obj)
        list1 = []
        for obj in patient_objs:
            session_total_time = get_session_total_time_previous_month(obj)
            total_time = get_mannual_total_time_previous_month(obj)
            total_monthly_time = total_time + session_total_time  
            list1.append(total_monthly_time)
        time_in_hrs_min = ':'.join((str(datetime.timedelta(seconds=sum(list1)))).split(":")[:-1])
        return time_in_hrs_min
    
    
class GetCareManagerListSerializer(serializers.ModelSerializer):
    caremanagers = serializers.SerializerMethodField() 
    
    class Meta:
        model = CareManager
        fields = ["caremanagers"]

    
    def get_caremanagers(self, obj):
        result = []
        zero_to_ten = self.context['zero_to_ten']
        ten_to_twenty = self.context['ten_to_twenty']
        above_twenty = self.context['above_twenty']
        caremanager_data = CareManager.objects.filter(hospital=obj.hospital)
        try:
            for caremanager in caremanager_data:
                current_month_patient_objs = Patient.objects.filter(caremanager_obj=caremanager)
                list1 = []
                for current_month_patient in current_month_patient_objs:
                    session_total_time = get_session_total_time_current_month(current_month_patient)
                    total_time = get_mannual_total_time_current_month(current_month_patient)
                    total_monthly_time = total_time + session_total_time  
                    list1.append(total_monthly_time)

                current_month_time_in_hrs_min = ':'.join((str(datetime.timedelta(seconds=sum(list1)))).split(":")[:-1])
                current_month_time_hrs = int(current_month_time_in_hrs_min.split(":")[0]) * 60
                current_month_time_min = int(current_month_time_in_hrs_min.split(":")[1])
                current_month_time_in_total_min = current_month_time_hrs + current_month_time_min
                
                previous_month_patient_objs = Patient.objects.filter(caremanager_obj=caremanager)
                list2 = []
                for previous_month_patient in previous_month_patient_objs:
                    session_total_time = get_session_total_time_previous_month(previous_month_patient)
                    total_time = get_mannual_total_time_previous_month(previous_month_patient)
                    total_monthly_time = total_time + session_total_time  
                    list2.append(total_monthly_time)
                previous_month_patient_objs = ':'.join((str(datetime.timedelta(seconds=sum(list2)))).split(":")[:-1])
                
                if zero_to_ten == '0-10' and current_month_time_in_total_min >= 0 and current_month_time_in_total_min <= 10:
                    data = {}
                    data['id'] = caremanager.id
                    data['caremanager_name'] = caremanager.user.get_full_name()
                    data['caremanager_email'] = caremanager.user.email
                    data['caremanager_contact'] = caremanager.contact
                    data['assigned_patient'] = caremanager.patients_care_manager.all().count()
                    data['previous_month_minutes'] = previous_month_patient_objs
                    data['current_month_minutes'] = current_month_time_in_total_min
                    result.append(data)
                    
                elif ten_to_twenty == '10-20' and current_month_time_in_total_min >= 11 and current_month_time_in_total_min < 20:
                    data = {}
                    data['id'] = caremanager.id
                    data['caremanager_name'] = caremanager.user.get_full_name()
                    data['caremanager_email'] = caremanager.user.email
                    data['caremanager_contact'] = caremanager.contact
                    data['assigned_patient'] = caremanager.patients_care_manager.all().count()
                    data['previous_month_minutes'] = previous_month_patient_objs
                    data['current_month_minutes'] = current_month_time_in_total_min
                    result.append(data)
                
                elif above_twenty == '20' and current_month_time_in_total_min >= 20:
                    data = {}
                    data['id'] = caremanager.id
                    data['caremanager_name'] = caremanager.user.get_full_name()
                    data['caremanager_email'] = caremanager.user.email
                    data['caremanager_contact'] = caremanager.contact
                    data['assigned_patient'] = caremanager.patients_care_manager.all().count()
                    data['previous_month_minutes'] = previous_month_patient_objs
                    data['current_month_minutes'] = current_month_time_in_total_min
                    result.append(data)
                    
            return result
        except Exception as e:
            return str(e)


class AssignPatientListSerializer(serializers.Serializer):
    patient_name = serializers.SerializerMethodField()
    provider_name = serializers.SerializerMethodField()
    caremanager_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PatientProviderMapping
        fields = ["patient_name", "provider_name", "caremanager_name"]
        
    def get_patient_name(self, obj):
        if obj:
            patient = obj.patient.user.get_full_name()
            return patient
        else:
            return None             
    
    def get_provider_name(self, obj):
        if obj:
            provider = obj.primary_provider.user.get_full_name()
            return provider
        else:
            return None
        
    def get_caremanager_name(self, obj):
        if obj:
            caremanager = obj.patient.caremanager_obj.user.get_full_name()
            return caremanager
        else:
            return None
    
    
    
class MultiSerializers(serializers.ModelSerializer):
    id=PatientSerializer
    user_id=serializers.SerializerMethodField()
    class Meta:
        model=[Patient,User]
        fields="__all__"
        