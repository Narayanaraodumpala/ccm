from apps.hospital.models import (
    Appointment,
    Hospital,
    HospitalBranch,
    Department,
    Medication,
    MedicationChronicCondition,
    Treatment,
    ChronicCondition,
    PatientChronicDisease, NPITaxonomy,
)
from apps.authentication.models import User
from apps.account_manager.models import Patient, Provider, PracticeAdmin, CareManager

from rest_framework import serializers

from apps.hospital.utils import user_type_hospital_exists


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = "__all__"

class HospitalPutSerializer(serializers.ModelSerializer):
    # internal hospital data -- get status of active-inactive of doctor & patient and total admins,

    class Meta:
        model = Hospital
        fields = '__all__'

class HospitalSerializer(serializers.ModelSerializer):
    # internal hospital data -- get status of active-inactive of doctor & patient and total admins,
    internal_hospital_data = serializers.SerializerMethodField()
    hospital_image = serializers.ImageField(required=False)
    hospital_branch_count = serializers.SerializerMethodField()
    system_id = serializers.SerializerMethodField()
    hospital_status = serializers.SerializerMethodField()

    class Meta:
        model = Hospital
        fields = [
            "id",
            "system_id",
            "npi_id",
            "hospital_name",
            "hospital_tax_id",
            "contact_person_name",
            "contact_number",
            "address_1",
            "address_2",
            "state_province_area",
            "zip_code",
            "city",
            "website_url",
            "hospital_status",
            "internal_hospital_data",
            "hospital_image",
            "hospital_branch_count",
            "taxonomy_id",
            "taxonomy_description"
        ]

    def get_system_id(self, obj):
        try:
            practice_admin = PracticeAdmin.objects.filter(hospital=obj.id).last()
            if practice_admin:
                return str(practice_admin.user.system_id)
            else:
                return 0
        except Exception as e:
            return 0

    def get_internal_hospital_data(self, obj):
        created_date = obj.created_at
        active_provider = Provider.objects.filter(hospital=obj, is_active=True, provider_status="ACTIVE").all().count()
        inactive_provider = Provider.objects.filter(hospital=obj, provider_status="INACTIVE").all().count()
        active_patient = Patient.objects.filter(hospital=obj, is_active=True, patient_status="ACTIVE").all().count()
        inactive_patient = Patient.objects.filter(hospital=obj, patient_status="INACTIVE").all().count()

        total_practice_admin = obj.practiceadmin_set.all().count()
        total_patients = Patient.objects.filter(hospital=obj).count()
        care_manager_count = CareManager.objects.filter(hospital=obj).count()

        # related to chronic disease, need to update the value in phase 2
        total_disease = 0
        return {
            "created_date": created_date,
            "active_provider": active_provider,
            "inactive_provider": inactive_provider,
            "active_patient": active_patient,
            "inactive_patient": inactive_patient,
            "total_practice_admin": total_practice_admin,
            "total_patients": total_patients,
            "total_disease": total_disease,
            "care_manager_count": care_manager_count
        }
        
    def get_hospital_branch_count(self, obj):
        count = None
        if obj:
            count = HospitalBranch.objects.filter(hospital=obj).all().count()
        return count
    
    def get_hospital_status(self, obj):
        return obj.hospital_status
            

class HospitalBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalBranch
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class TreatmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Treatment
        fields = "__all__"


class CronicConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChronicCondition
        fields = "__all__"


class HospitaldataListSerializer(serializers.ModelSerializer):
    patients_count = serializers.SerializerMethodField()
    caremanager_count = serializers.SerializerMethodField()

    class Meta:
        model = Hospital
        fields = [
            "id",
            "hospital_name",
            "npi_id",
            "city",
            "created_at",
            "patients_count",
            "caremanager_count",
            "hospital_status",
        ]

    def get_patients_count(self, obj):
        patient = obj.patient_info.all().count()
        return patient

    def get_caremanager_count(self, obj):
        care_manager = obj.caremanager_info.all().count()
        return care_manager


class HospitalRelatedUserSerializer(serializers.ModelSerializer):
    user_type = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    contact_number = serializers.SerializerMethodField()
    user_type_id = serializers.SerializerMethodField()
    user_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["user_type_id", "user_type", "email", "full_name", "contact_number","user_status"]

    def get_user_type_id(self, obj):
        user_type = obj.user_type
        if user_type == "CAREMANAGER":
            cm = CareManager.objects.filter(user=obj).last()
            if cm:
                return cm.id
            else:
                return 0
        elif user_type == "PROVIDER":
            prd = Provider.objects.filter(user=obj).last()
            if prd:
                return prd.id
            else:
                return 0
        elif user_type == "PRACTICEADMIN":
            pa = PracticeAdmin.objects.filter(user=obj).last()
            if pa:
                return pa.id
            else:
                return 0
        else:
            return 0

    def get_user_type(self, obj):
        hospital = self.context.get("hospital_obj")
        if user_type_hospital_exists(hospital, obj):
            return obj.get_user_type_display()

    def get_email(self, obj):
        hospital = self.context.get("hospital_obj")
        if user_type_hospital_exists(hospital, obj):
            return obj.email

    def get_full_name(self, obj):
        hospital = self.context.get("hospital_obj")
        if user_type_hospital_exists(hospital, obj):
            return obj.get_full_name()

    def get_contact_number(self, obj):
        try:
            hospital = self.context.get("hospital_obj")
            if user_type_hospital_exists(hospital, obj):
                user, user_type = user_type_hospital_exists(hospital, obj)
                if user_type == "CAREMANAGER":
                    return obj.care_users.contact
                elif user_type == "PROVIDER":
                    provider = Provider.objects.filter(user=obj).last()
                    return provider.contact_number
                elif user_type == "PRACTICEADMIN":
                    practice_admin = PracticeAdmin.objects.filter(user=obj).last()
                    return practice_admin.contact_number
        except Exception as e:
            return 0
        
        
    def get_user_status(self, obj):
        try:
            hospital = self.context.get("hospital_obj")
            if user_type_hospital_exists(hospital, obj):
                user, user_type = user_type_hospital_exists(hospital, obj)
                if user_type == "CAREMANAGER":
                    care_manager = CareManager.objects.filter(user=obj).last()
                    return care_manager.get_care_manager_status_display()
                elif user_type == "PROVIDER":
                    provider = Provider.objects.filter(user=obj).last()
                    return provider.get_provider_status_display()
                elif user_type == "PRACTICEADMIN":
                    practice_admin = PracticeAdmin.objects.filter(user=obj).last()
                    return practice_admin.get_practice_admin_status_display()
        except Exception as e:
            return 0


class HospitalBranchLocationSerializer(serializers.ModelSerializer):
    branch_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    contact_number = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    branch_id = serializers.SerializerMethodField()
    hospital_branch_status = serializers.SerializerMethodField()

    class Meta:
        model = Hospital
        fields = ["branch_id", "branch_name", "email", "contact_number", "location", "hospital_branch_status"]

    def get_branch_id(self, obj):
        return obj.id

    def get_branch_name(self, obj):
        return obj.branch_name

    def get_email(self, obj):
        return obj.contact_email

    def get_contact_number(self, obj):
        return obj.contact_number

    def get_location(self, obj):
        return obj.location
    
    def get_hospital_branch_status(self, obj):
        return obj.hospital_branch_status


class HospitalTestSerializer(serializers.ModelSerializer):
    hospital_create = serializers.SerializerMethodField()
    patient_create = serializers.SerializerMethodField()
    provider_create = serializers.SerializerMethodField()

    class Meta:
        model = Hospital
        fields = ["id", "hospital_create", "patient_create", "provider_create"]

    def get_hospital_create(self, obj):
        return obj.created_at

    def get_patient_create(self, obj):
        provider = obj.provider_hospital.all()
        for i in provider:
            return i.created_at

    def get_provider_create(self, obj):
        patient = obj.patient_info.all()
        for i in patient:
            return i.created_at

class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = "__all__"


class PatientChronicDiseaseCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = PatientChronicDisease
        fields = ["patient", "chronic", "name", "description", "file"]


class ChronicConditionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChronicCondition
        fields = ["id", "disease_name", "description"]


# class PatientChronicDiseaseListSerializer(serializers.ModelSerializer):
#     chronic = ChronicConditionSerializer()

#     class Meta:
#         model = PatientChronicDisease
#         fields = ["id", "patient", "chronic", "name", "description", "file"]



class PatientChronicDiseaseListSerializer(serializers.ModelSerializer):
    has_disease = serializers.SerializerMethodField()
    patient_chronic = serializers.SerializerMethodField()

    class Meta:
        model = ChronicCondition
        fields = ['id', 'disease_name', 'patient_chronic', 'has_disease']

    def get_has_disease(self, obj):
        patient_id = self.context.get('patient_id')
        pcd = PatientChronicDisease.objects.filter(patient_id=patient_id, chronic=obj)
        if pcd:
            return True
        else:
            return False

    def get_patient_chronic(self, obj):
        chronic_list = []

        patient_id = self.context.get('patient_id')
        pcd = PatientChronicDisease.objects.filter(patient_id=patient_id, chronic=obj, is_active=True).order_by('-created_at')[:5]
        if pcd:
            for cd in pcd:
                pcd_dict = {}
                pcd_dict.update({
                    'id': cd.id,
                    'name': cd.name,
                    'description': cd.description,
                    'file': cd.file if cd.file else None,
                    'disease_name': cd.chronic.disease_name,
                    'created_at': cd.created_at
                })
                chronic_list.append(pcd_dict)
        return chronic_list


class PatientChronicDiseaseUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = PatientChronicDisease
        fields = ["patient", "chronic", "name", "description", "file"]


class PatientChronicDiseaseSerializer(serializers.ModelSerializer):
    has_disease = serializers.SerializerMethodField()

    class Meta:
        model = ChronicCondition
        fields = ["id", "disease_name", "has_disease"]

    def get_has_disease(self, obj):
        result = False
        patient_id = self.context.get('patient_id')
        pcd = PatientChronicDisease.objects.filter(patient_id=patient_id, chronic=obj).last()
        if pcd:
            result = True
        return result


class AssignChronicConditionSerializer(serializers.ModelSerializer):

    class Meta:
        model = PatientChronicDisease
        fields = ["patient", "chronic"]


class NPITaxonomySerializer(serializers.ModelSerializer):

    class Meta:
        model = NPITaxonomy
        fields = ["medicare_specialty_code", "medicare_provider_supplier_type_description", "provider_taxonomy_code", "provider_taxonomy_description"]


class PatientMedicationChronicDiseaseListSerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicationChronicCondition
        fields = ['id', 'disease_name']


class MedicationListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Medication
        fields = '__all__'



