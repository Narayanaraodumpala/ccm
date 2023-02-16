import datetime
import pandas as pd

from apps.account_manager.utils import build_calllog_data, build_task_data
from itertools import chain
from datetime import date, timedelta 
from dateutil.relativedelta import relativedelta


import django_filters
from django_filters import OrderingFilter, filters
from rest_framework.pagination import PageNumberPagination

from apps.account_manager.models import PatientSession, PracticeAdmin, Provider, CareManager, Patient
from apps.patient.models import AnnualWellnessVisitCallLog, AnnualWellnessVist, AssessmentCallLog, CareManagerNotes, MedicalConditionCallLog, PatientCallLog, SelfManagementPlanCallLog, Task, PatientOutreach, VitalCallLog, Problems
from apps.assessment.models import Assessment

def get_patient_personal_info(obj):
    personal_info = {}
    name = obj.user.first_name + " " + obj.user.last_name
    address = get_patient_contact_detail(obj)
    gender = obj.gender
    email =  obj.user.email
    cell_phone = get_patient_cell_phone(obj)
    home_phone = get_patient_home_phone(obj)
    beneficiiary_status = obj.get_patient_status_display()
    # pcp
    personal_info["name"] = name
    personal_info["address"] = address
    personal_info["gender"] = gender
    personal_info["email"] = email
    personal_info["cell_phone"] = cell_phone
    personal_info["home_phone"] = home_phone
    personal_info["beneficiiary_status"] = beneficiiary_status
    return personal_info


def get_patient_contact_detail(obj):
    try:
        if obj.patient_contact_detail.first():
            address_1 = obj.patient_contact_detail.first().address_1, ''
            city = obj.patient_contact_detail.first().city, 'ss'
            state = obj.patient_contact_detail.first().state, None
            zip_code = obj.patient_contact_detail.first().zip_code, None
            address = address_1 + " " + city + ", " + state + "," + zip_code
            return address
    except Exception as e:
        return None

def get_patient_cell_phone(obj):
    try:
        if obj.patient_contact_detail.first():
            return obj.patient_contact_detail.first().cell_phone
    except Exception as e:
        return None

def get_patient_home_phone(obj):
    try:
        if obj.patient_contact_detail.first():
            return obj.patient_contact_detail.first().home_phone
    except Exception as e:
        return None


class AnnualWellnessVisitFilter(django_filters.FilterSet):
    from_date = filters.DateFilter(field_name='created_at', label='from_date', lookup_expr='gte')
    to_date = filters.DateFilter(field_name='created_at', label='to_date', lookup_expr='lte')
    
    order_by_field = 'ordering'

    class Meta:
        model = AnnualWellnessVist
        fields = ['id', 'created_at']


class PatientTaskFilter(django_filters.FilterSet):
    from_date = filters.DateFilter(field_name='created_at', label='from_date', lookup_expr='gte')
    to_date = filters.DateFilter(field_name='created_at', label='to_date', lookup_expr='lte')

    order_by_field = 'ordering'

    class Meta:
        model = Task
        fields = ['id', 'created_at']


def get_last_updated_object(patient, related_model_name):
    last_modified_at = patient.modified_at
    last_created_at = patient.created_at
    last_created_by = patient.created_by
    
    for i in related_model_name:
        if i == 'ProgramInformation':
            obj = patient.programinformation_set.last()
            if obj:
                obj_created_at = patient.programinformation_set.latest('created_at').created_at
                obj_modified_at = patient.programinformation_set.latest('modified_at').modified_at
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                            last_created_by = obj.created_by
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                            last_created_by = obj.created_by
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at
        elif i == 'AnnualWellnessVist':
            obj = patient.awv_patient.last()
            if obj:
                obj_created_at = patient.awv_patient.latest('created_at').created_at
                obj_modified_at = patient.awv_patient.latest('modified_at').modified_at
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'BMI':
            obj = patient.patient_bmi.last()
            if obj:
                obj_created_at = patient.patient_bmi.latest('created_at')
                obj_modified_at = patient.patient_bmi.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'BloodPressure':
            obj = patient.patient_blood_pressure.last()
            if obj:
                obj_created_at = patient.patient_blood_pressure.latest('created_at')
                obj_modified_at = patient.patient_blood_pressure.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at
        elif i == 'BloodGlucose':
            obj = patient.patient_blood_glucose.last()
            if obj:
                obj_created_at = patient.patient_blood_glucose.latest('created_at')
                obj_modified_at = patient.patient_blood_glucose.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'PulseOx':
            obj = patient.patient_pulseOx.last()
            if obj:
                obj_created_at = patient.patient_pulseOx.latest('created_at')
                obj_modified_at = patient.patient_pulseOx.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'Cholesterol':
            obj = patient.patient_cholesterol.last()
            if obj:
                obj_created_at = patient.patient_cholesterol.latest('created_at')
                obj_modified_at = patient.patient_cholesterol.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'HBA1C':
            obj = patient.patient_hba1c.last()
            if obj:
                obj_created_at = patient.patient_hba1c.latest('created_at')
                obj_modified_at = patient.patient_hba1c.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at            

        elif i == 'Notes':
            obj = patient.notes_set.last()
            if obj:
                obj_created_at = patient.notes_set.latest('created_at')
                obj_modified_at = patient.notes_set.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'Goal':
            obj = patient.patient_goal.last()
            if obj:
                obj_created_at = patient.patient_goal.last().created_at
                obj_modified_at = patient.patient_goal.last().modified_at
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at            

        elif i == 'Intervention':
            obj = patient.intervention_set.last()
            if obj:
                obj_created_at = patient.intervention_set.last().created_at
                obj_modified_at = patient.intervention_set.last().modified_at
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                            last_created_by = obj.created_by
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                            last_created_by = obj.created_by
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'Task':
            obj = patient.task_set.last()
            if obj:
                obj_created_at = patient.task_set.last().created_at
                obj_modified_at = patient.task_set.last().modified_at
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'MedicationNotes':
            obj = patient.medicationnotes_set.last()
            if obj:
                obj_created_at = patient.medicationnotes_set.last().created_at
                obj_modified_at = patient.medicationnotes_set.last().modified_at
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'PatientCallLog':
            obj = patient.patient_patientcall_log.last()
            if obj:
                obj_created_at = patient.patient_patientcall_log.latest('created_at')
                obj_modified_at = patient.patient_patientcall_log.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'VitalCallLog':
            obj = patient.patient_vitalcall_log.last()
            if obj:
                obj_created_at = patient.patient_vitalcall_log.latest('created_at')
                obj_modified_at = patient.patient_vitalcall_log.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'MedicalConditionCallLog':
            obj = patient.patient_medicalconditioncalllog.last()
            if obj:
                obj_created_at = patient.patient_medicalconditioncalllog.latest('created_at')
                obj_modified_at = patient.patient_medicalconditioncalllog.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'AssessmentCallLog':
            obj = patient.patient_assessmentcalllog.last()
            if obj:
                obj_created_at = patient.patient_assessmentcalllog.latest('created_at')
                obj_modified_at = patient.patient_assessmentcalllog.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'AnnualWellnessVisitCallLog':

            obj = patient.patient_annualwellnessvisit_calllog.last()
            if obj:
                obj_created_at = patient.patient_annualwellnessvisit_calllog.latest('created_at')
                obj_modified_at = patient.patient_annualwellnessvisit_calllog.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'SelfManagementPlanCallLog':
            obj = patient.patient_selfmanagementplancalllog.last()
            if obj:
                obj_created_at = patient.patient_selfmanagementplancalllog.latest('created_at')
                obj_modified_at = patient.patient_selfmanagementplancalllog.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'PatientOutreach':

            obj = patient.patientoutreach_set.last()
            if obj:
                obj_created_at = patient.patientoutreach_set.latest('created_at')
                obj_modified_at = patient.patientoutreach_set.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'Problems': 
            obj = patient.patient_problems.last()
            if obj:
                obj_created_at = patient.patient_problems.latest('created_at')
                obj_modified_at = patient.patient_problems.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'Allergies':
            obj = patient.patient_allergies.last()
            if obj:
                obj_created_at = patient.patient_allergies.latest('created_at')
                obj_modified_at = patient.patient_allergies.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'Immunization':
            obj = patient.patient_immunization.last()
            if obj:
                obj_created_at = patient.patient_immunization.latest('created_at')
                obj_modified_at = patient.patient_immunization.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'LabReports':
            obj = patient.patient_labreport.last()
            if obj:
                obj_created_at = patient.patient_labreport.last().created_at
                obj_modified_at = patient.patient_labreport.last().modified_at
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'Procedures':
            obj =  patient.patient_procedures.last()
            if obj:
                obj_created_at = patient.patient_procedures.latest('created_at')
                obj_modified_at = patient.patient_procedures.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'PatientDocs':
            obj = patient.patient_docs.last()
            if obj:
                obj_created_at = patient.patient_docs.latest('created_at')
                obj_modified_at = patient.patient_docs.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'Appointment':
            obj = patient.appointment_set.last()
            if obj:
                obj_created_at = patient.appointment_set.last().created_at
                obj_modified_at = patient.appointment_set.last().modified_at
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'DoctorRating': 
            obj = patient.doctorrating_set.last() 
            if obj:
                obj_created_at = patient.doctorrating_set.last().created_at
                obj_modified_at = patient.doctorrating_set.last().modified_at
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'Treatment':
            obj = patient.patient_treatment.last()
            if obj:
                obj_created_at = patient.patient_treatment.latest('created_at')
                obj_modified_at = patient.patient_treatment.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'PatientChronicDisease':
            obj = patient.chronic_patient.last()
            if obj:
                obj_created_at = patient.chronic_patient.latest('created_at')
                obj_modified_at = patient.chronic_patient.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'Medication':
            obj = patient.patient_medication.last()
            if obj:
                obj_created_at =  patient.patient_medication.latest('created_at')
                obj_modified_at =  patient.patient_medication.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif  i == 'PatientProviderMapping':
            obj = patient.patient_patientprovidermapping.last() 
            if obj:
                obj_created_at = patient.patient_patientprovidermapping.latest('created_at')
                obj_modified_at = patient.patient_patientprovidermapping.latest('modified_at') 
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'PatientContactDetails':
            obj = patient.patient_contact_detail.last()
            if obj:
                obj_created_at = patient.patient_contact_detail.latest('created_at')
                obj_modified_at = patient.patient_contact_detail.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'SelfManagementPlan':
            obj = patient.patient.last()
            if obj:
                obj_created_at =  patient.patient.latest('created_at')
                obj_modified_at = patient.patient.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'Assessment':
            obj = patient.patient_assessment.last()
            if obj:
                obj_created_at = patient.patient_assessment.latest('created_at')
                obj_modified_at = patient.patient_assessment.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

        elif i == 'PatientQuestionAnswer':
            obj = patient.patient_info.last()
            if obj:
                obj_created_at = patient.patient_info.latest('created_at')
                obj_modified_at = patient.patient_info.latest('modified_at')
                try:
                    if last_created_at < obj_created_at:
                            last_created_at = obj_created_at
                    if last_modified_at < obj_modified_at:
                            last_modified_at = obj_modified_at
                except Exception as e:
                    if obj_created_at.created_at:
                        if last_created_at < obj_created_at.created_at:
                            last_created_at = obj_created_at.created_at
                    if obj_modified_at.modified_at:
                        if last_modified_at < obj_modified_at.modified_at:
                            last_modified_at = obj_modified_at.modified_at

    return str(last_created_at), str(last_modified_at), last_created_by


def create_scheduled_outreach_object(instance):
    try:
        PatientOutreach.objects.create(
            patient=instance.patient,
            contact_date=instance.schedule_follow_up_date,
            schedule_follow_up_date=None,
            contact_type=instance.contact_type,
            resolution_action=instance.resolution_action,
            outcome=instance.outcome,
            provider=instance.provider,
            time_spent=None,
            notes=None,
            care_program=instance.care_program,
            care_program_from_date=instance.care_program_from_date,
            care_program_to_date=instance.care_program_to_date,
            care_member=instance.care_member,
            patientoutreach_status=instance.patientoutreach_status,
            outreach_status="PENDING",
        )
    except Exception as e:
        print(str(e))
    return True


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'size'  # items per page
    

def taskoutreachsearch(self, obj):
    tasks = Task.objects.filter(care_manager=obj)
    outreaches = PatientOutreach.objects.filter(care_manager=obj)
    cm_notes = CareManagerNotes.objects.filter(care_manager=obj)
    
    task_name = self.request.query_params.get('task_name')            
    patient_name = self.request.query_params.get('patient_name')
    task_type = self.request.query_params.get('task_type')
    from_date = self.request.query_params.get('from_date',None)
    to_date = self.request.query_params.get('to_date',None)
    
    if patient_name:
        tasks = Task.objects.filter(care_manager=obj, patient__user__first_name__icontains=patient_name)
        outreaches = PatientOutreach.objects.filter( care_manager=obj,patient__user__first_name__icontains=patient_name)
        cm_notes = CareManagerNotes.objects.filter( care_manager=obj,patient__user__first_name__icontains=patient_name)
        
    if task_name:
        tasks = Task.objects.filter(care_manager=obj, name__icontains=task_name)
        outreaches = PatientOutreach.objects.filter(care_manager=obj, notes__icontains=task_name)
        cm_notes = CareManagerNotes.objects.filter(care_manager=obj, notes__icontains=task_name)  
          
    if from_date and to_date:
        tasks = Task.objects.filter(care_manager=obj, modified_at__date__range=[from_date, to_date] )
        outreaches = PatientOutreach.objects.filter(care_manager=obj, modified_at__date__range=[from_date, to_date])
        cm_notes = PatientOutreach.objects.filter(care_manager=obj, modified_at__date__range=[from_date, to_date])
        
              
    if task_type == "Task":
        combined_queryset = list(chain(tasks))
    elif task_type == "Outreach":
        combined_queryset = list(chain(outreaches)) 
    elif task_type == "Notes":
        combined_queryset = list(chain(cm_notes))     
    else:
        combined_queryset = list(chain(tasks, outreaches, cm_notes))      
    print(combined_queryset)            
    result = build_task_data(combined_queryset)
    return result

def get_mannual_total_time(obj):
    result_sum = 0
    try:
        vcall = VitalCallLog.objects.filter(patient=obj)
        mcall = MedicalConditionCallLog.objects.filter(patient=obj)
        acall = Assessment.objects.filter(patient=obj)
        awvcall = AnnualWellnessVisitCallLog.objects.filter(patient=obj)
        smpcall = SelfManagementPlanCallLog.objects.filter(patient=obj)
        taskcall = Task.objects.filter(patient=obj)
        outreachcall = PatientOutreach.objects.filter(patient=obj)            
        total_vcall_duration = sum([i.call_duration.seconds for i in vcall])
        total_mcall_duration = sum([i.call_duration.seconds for i in mcall])
        total_acall_duration = sum([i.manual_time.seconds for i in acall])
        total_awvcall_duration = sum([i.call_duration.seconds for i in awvcall])
        total_smpcall_duration = sum([i.call_duration.seconds for i in smpcall])
        total_taskcall_duration = sum([i.time_spent.seconds for i in taskcall])
        total_outreachcall_duration = sum([i.time_spent.seconds for i in outreachcall])
        
        total_call_duration = total_vcall_duration + total_mcall_duration + total_acall_duration + total_awvcall_duration + total_smpcall_duration + total_taskcall_duration + total_outreachcall_duration
        
        return total_call_duration
    
    except Exception as e:
        return result_sum
    

def get_session_total_time(obj):
    p_session = PatientSession.objects.filter(patient=obj)
    total_session_duration = sum([i.duration.seconds for i in p_session])
    return total_session_duration    



def taskoutreachcalllog_combine(self, obj, patient_id):
    hospital_care_manager = obj.hospital
    patient = Patient.objects.filter(id=patient_id).last()
    patientcalllog = PatientCallLog.objects.filter(patient = patient, patient__hospital=hospital_care_manager).exclude(patient__patient_status="SUSPENDED")
    tasks = Task.objects.filter(care_manager=obj, patient = patient )
    outreaches = PatientOutreach.objects.filter(care_manager=obj, patient = patient )
    cm_notes = CareManagerNotes.objects.filter(care_manager=obj, patient = patient)
    
    combined_queryset = list(chain(tasks, outreaches, patientcalllog, cm_notes))      
    print(combined_queryset)            
    result = build_calllog_data(combined_queryset)
    return result



class FilterData(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr = 'icontains', label="name")
    description = django_filters.CharFilter(lookup_expr = 'icontains', label="description")
    created_at = django_filters.CharFilter(lookup_expr = 'icontains', label="created_at")




class FilterSession(django_filters.FilterSet):
    session_id = django_filters.CharFilter(lookup_expr='exact')


def get_call_types(obj, vcall, mcall, acall, awvcall, smpcall, taskcall, outreachcall):

    result_sum = []

    for vcl in vcall:
        data_dict = {}
        data_dict["user_email"] = str(obj.user.email)
        data_dict["type"] = "Vital"
        if vcl.call_duration:
            time_spent = vcl.call_duration.seconds // 60
            data_dict["time_spent"] = time_spent
        else:
            data_dict["time_spent"] = 0
        data_dict["Created_at"] = vcl.created_at
        result_sum.append(data_dict)

    for mcl in mcall:
        data_dict = {}
        data_dict["user_email"] = str(obj.user.email)
        data_dict["type"] = "Clinical Profile"
        if mcl.call_duration:
            time_spent = mcl.call_duration.seconds // 60
            data_dict["time_spent"] = time_spent
        else:
            data_dict["time_spent"] = 0
        data_dict["Created_at"] = mcl.created_at
        result_sum.append(data_dict)

    for acl in acall:
        data_dict = {}
        data_dict["user_email"] = str(obj.user.email)
        data_dict["type"] = "Assessment"
        if acl.manual_time:
            time_spent = acl.manual_time.seconds // 60
            data_dict["time_spent"] = time_spent
        else:
            data_dict["time_spent"] = 0
        data_dict["Created_at"] = acl.created_at
        result_sum.append(data_dict)

    for amvcl in awvcall:
        data_dict = {}
        data_dict["user_email"] = str(obj.user.email)
        data_dict["type"] = "Care Gap"
        if amvcl.call_duration:
            time_spent = amvcl.call_duration.seconds // 60
            data_dict["time_spent"] = time_spent
        else:
            data_dict["time_spent"] = 0
        data_dict["Created_at"] = amvcl.created_at
        result_sum.append(data_dict)

    for smpcl in smpcall:
        data_dict = {}
        data_dict["user_email"] = str(obj.user.email)
        data_dict["type"] = "Self Management Plan"
        if smpcl.call_duration:
            time_spent = smpcl.call_duration.seconds // 60
            data_dict["time_spent"] = time_spent
        else:
            data_dict["time_spent"] = 0
        data_dict["Created_at"] = smpcl.created_at
        result_sum.append(data_dict)

    # for pcl in pcall:
    #     data_dict = {}
    #     data_dict["user_email"] = str(obj.user.email)
    #     data_dict["type"] = "CallLog"
    #     time_spent = pcl.call_duration.seconds // 60
    #     data_dict["time_spent"] = time_spent
    #     # startTime = (
    #     #     (datetime.datetime.min + time_spent).time().replace(microsecond=0)
    #     # )
    #     # data_dict["time_spent"] = str(startTime)
    #     data_dict["Created_at"] = pcl.created_at
    #     result_sum.append(data_dict)

    for taskcl in taskcall:
        data_dict = {}
        data_dict["user_email"] = str(obj.user.email)
        data_dict["type"] = "Task"
        if taskcl.time_spent:
            time_spent = taskcl.time_spent.seconds // 60
            data_dict["time_spent"] = time_spent
        else:
            data_dict["time_spent"] = 0
        data_dict["Created_at"] = taskcl.created_at
        result_sum.append(data_dict)

    for outeachcl in outreachcall:
        data_dict = {}
        data_dict["user_email"] = str(obj.user.email)
        data_dict["type"] = "Intervention"
        if outeachcl.time_spent:
            time_spent = outeachcl.time_spent.seconds // 60
            data_dict["time_spent"] = time_spent
        else:
            data_dict["time_spent"] = 0
        data_dict["Created_at"] = outeachcl.created_at
        result_sum.append(data_dict)

    return result_sum


def get_session_total_time_current_month(obj):
    today = datetime.date.today()
    p_session = PatientSession.objects.filter(patient=obj, created_at__month = today.month)
    total_session_duration = sum([i.duration.seconds for i in p_session])
    return total_session_duration 


def get_mannual_total_time_current_month(obj):
    today = datetime.date.today()
    result_sum = 0
    try:
        vcall = VitalCallLog.objects.filter(patient=obj, created_at__month = today.month)
        mcall = MedicalConditionCallLog.objects.filter(patient=obj, created_at__month = today.month)
        acall = AssessmentCallLog.objects.filter(patient=obj, created_at__month = today.month)
        awvcall = AnnualWellnessVisitCallLog.objects.filter(patient=obj, created_at__month = today.month)
        smpcall = SelfManagementPlanCallLog.objects.filter(patient=obj, created_at__month = today.month)
        taskcall = Task.objects.filter(patient=obj, created_at__month = today.month)
        outreachcall = PatientOutreach.objects.filter(patient=obj, created_at__month = today.month)            
        total_vcall_duration = sum([i.call_duration.seconds for i in vcall])
        total_mcall_duration = sum([i.call_duration.seconds for i in mcall])
        total_acall_duration = sum([i.call_duration.seconds for i in acall])
        total_awvcall_duration = sum([i.call_duration.seconds for i in awvcall])
        total_smpcall_duration = sum([i.call_duration.seconds for i in smpcall])
        total_taskcall_duration = sum([i.time_spent.seconds for i in taskcall])
        total_outreachcall_duration = sum([i.time_spent.seconds for i in outreachcall])
        
        total_call_duration = total_vcall_duration + total_mcall_duration + total_acall_duration + total_awvcall_duration + total_smpcall_duration + total_taskcall_duration + total_outreachcall_duration
        return total_call_duration    
    except Exception as e:
        return result_sum
    
def get_session_total_time_previous_month(obj):
    prev = date.today().replace(day=1) - timedelta(days=1)
    p_session = PatientSession.objects.filter(patient=obj, created_at__month = prev.month)
    total_session_duration = sum([i.duration.seconds for i in p_session])
    return total_session_duration  

def get_mannual_total_time_previous_month(obj):
    prev = date.today().replace(day=1) - timedelta(days=1)
    result_sum = 0
    try:
        vcall = VitalCallLog.objects.filter(patient=obj, created_at__month = prev.month)
        mcall = MedicalConditionCallLog.objects.filter(patient=obj, created_at__month = prev.month)
        acall = AssessmentCallLog.objects.filter(patient=obj, created_at__month = prev.month)
        awvcall = AnnualWellnessVisitCallLog.objects.filter(patient=obj, created_at__month = prev.month)
        smpcall = SelfManagementPlanCallLog.objects.filter(patient=obj, created_at__month = prev.month)
        taskcall = Task.objects.filter(patient=obj, created_at__month = prev.month)
        outreachcall = PatientOutreach.objects.filter(patient=obj, created_at__month = prev.month)            
        total_vcall_duration = sum([i.call_duration.seconds for i in vcall])
        total_mcall_duration = sum([i.call_duration.seconds for i in mcall])
        total_acall_duration = sum([i.call_duration.seconds for i in acall])
        total_awvcall_duration = sum([i.call_duration.seconds for i in awvcall])
        total_smpcall_duration = sum([i.call_duration.seconds for i in smpcall])
        total_taskcall_duration = sum([i.time_spent.seconds for i in taskcall])
        total_outreachcall_duration = sum([i.time_spent.seconds for i in outreachcall])
        
        total_call_duration = total_vcall_duration + total_mcall_duration + total_acall_duration + total_awvcall_duration + total_smpcall_duration + total_taskcall_duration + total_outreachcall_duration
        return total_call_duration    
    except Exception as e:
        return result_sum

def get_weekends_weedays(key, from_date, to_date):
    if len(key) > 1:
        if key[0] == 'weekday' and key[1] == 'weekend':
            weekday_weekend = pd.bdate_range(start=from_date, end=to_date, freq="C", weekmask="Mon Tue Wed Thu Fri Sat Sun")
            return key, weekday_weekend
    else:
        if key[0] == 'weekend':
            weekends = pd.bdate_range(start=from_date, end=to_date, freq="C", weekmask="Sat Sun")
            return key, weekends
        elif key[0] == 'weekday':
            weekdays = pd.bdate_range(start=from_date, end=to_date, freq="C", weekmask="Mon Tue Wed Thu Fri")
            return key, weekdays

def get_days(key, from_date, to_date):
    key = [key[i][:3].title() for i in range(len(key))]
    key = ' '.join(key)
    weekdays = pd.bdate_range(start=from_date, end=to_date, freq="C", weekmask=key)
    return key, weekdays

def get_next_months_date(from_date, to_date):
    next_months_date = []
    while from_date <= to_date:
        next_months_date.append(from_date)
        from_date += relativedelta(months=1)
    return next_months_date

def get_bi_weekly_days(key, from_date, to_date):
    keys = [key[i][:3].title() for i in range(len(key))]
    if len(keys) == 1:
        key = "2W-"+' '.join(keys)
        date_rng=pd.date_range(start=from_date,end=to_date, freq=key)
        return date_rng
    else:
        bi_weekly = []
        for key in keys:
            date_rng=pd.date_range(start=from_date,end=to_date, freq="2W-"+key)
            for i in date_rng:
                bi_weekly.append(i.date())
        return bi_weekly
