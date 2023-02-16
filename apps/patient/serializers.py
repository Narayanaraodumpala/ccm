import datetime
import calendar
from django.conf import settings

from itertools import chain

from django.utils import timezone
from django.forms.models import model_to_dict
from apps.hospital.models import HospitalBranch, Treatment, ChronicCondition

from apps.hospital.models import Treatment, Medication
from rest_framework import serializers

from apps.account_manager.utils import build_task_data

from apps.patient.models import (
    AnnualWellnessVisitCallLog,
    AssessmentCallLog,
    CareManagerNotes,
    DailyGoalTask,
    DailyOutreach,
    GoalTask,
    PatientOutreach,
    ProgramInformation,
    MedicationNotes,
    PatientCallLog,
    SelfManagementPlanCallLog,
    ViewLogs,
    VitalCallLog,
    MedicalConditionCallLog,
    Problems,
    Allergies,
    Immunization,
    LabReports,
    Procedures,
    PatientDocs,
    AWVWho,
    AWVHowOften,
    ScreeningWhoOften,
    GeneralNotesCallLog,
    Problems,
    WeeklyOutreach,
)
from apps.patient.models import (
    Intervention,
    AnnualWellnessVist,
    BMI,
    BloodPressure,
    BloodGlucose,
    PulseOx,
    HBA1C,
    Cholesterol,
    Notes,
    Goal,
    Task,
    ScreeningName,
)

from apps.hospital.models import Appointment
from apps.patient.models import (
    Intervention,
    StepsToAchieveGoal,
    GoalChallenges,
    Assistance,
    ProgramInformationType,
)

from apps.account_manager.models import (
    CareManager,
    Patient,
    PatientProviderMapping,
    PatientContactDetails,
    PatientSession,
)
from apps.patient.helper import get_user_full_name

from apps.assessment.models import Assessment

from .utils import (
    get_days,
    get_patient_personal_info,
    get_session_total_time,
    get_mannual_total_time,
    get_call_types,
    get_weekends_weedays,
    get_next_months_date,
    get_bi_weekly_days,
)


class ListPatientAssessmentSerializer(serializers.ModelSerializer):
    assessment_name	 = serializers.SerializerMethodField()
    assessment_status = serializers.SerializerMethodField()
    time_spent = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
  
    class Meta:
        model = Assessment
        fields = ["assessment_name", "date", "score", "assessment_status", "time_spent", "severity"]

    def get_assessment_name(self, obj):
        return obj.question_category.question_category

    def get_assessment_status(self, obj):
        return obj.get_assessment_status_display()
        
    def get_time_spent(self, obj):
        if obj.manual_time:
            return obj.manual_time.seconds // 60
        else:
            return None 
    
    def get_date(self, obj):
        return obj.created_at.date()



class ProgramInformationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramInformationType
        fields = ["id", "program_name"]


class ProgramInformationTypeDetailSerializer(serializers.ModelSerializer):
    program_type = serializers.SerializerMethodField()
    program_status = serializers.SerializerMethodField()

    class Meta:
        model = ProgramInformation
        fields = ["id", "patient", "program_type", "date", "program_status"]

    def get_program_type(self, obj):
        try:
            p_type = obj.program_type.program_name
            return p_type
        except Exception as e:
            return None

    def get_program_status(self, obj):
        try:
            return obj.get_program_status_display()
        except Exception as e:
            return None


class ProgramInformationSerializer(serializers.ModelSerializer):
    # program_type = serializers.SerializerMethodField()

    class Meta:
        model = ProgramInformation
        fields = ["patient", "program_type", "date", "program_status"]


class InterventionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intervention
        fields = "__all__"


class ShowPatientStatsSerializer(serializers.ModelSerializer):
    total_patients_count = serializers.SerializerMethodField()
    enroll_patients_count = serializers.SerializerMethodField()
    inactive_patients_count = serializers.SerializerMethodField()
    not_reachable_patients_count = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = (
            "total_patients_count",
            "enroll_patients_count",
            "inactive_patients_count",
            "not_reachable_patients_count",
        )

    def get_total_patients_count(self, obj):
        result = 0
        try:
            patients = Patient.objects.filter(hospital=obj.hospital, caremanager_obj=obj).count()
            return patients
            # care_manager_hopital_branch = obj.hospital.hospital_branch.filter(care_manager=obj)
            # patient = Patient.objects.filter(hospital=obj.hospital, caremanager__in=care_manager_hopital_branch).count()
        except Exception as e:
            return result

    def get_enroll_patients_count(self, obj):
        result = 0
        try:
            patients = Patient.objects.filter(hospital=obj.hospital, caremanager_obj=obj)
            ccm_enrolled_patients = ProgramInformation.objects.filter(program_type__program_name='CCM',program_status='ACTIVE',patient__in=patients).count()
            # care_manager_hopital_branch = obj.hospital.hospital_branch.filter(care_manager=obj)
            # patients = Patient.objects.filter(hospital=obj.hospital, caremanager__in=care_manager_hopital_branch)
            # ccm_active_patient = ProgramInformation.objects.filter(program_type__program_name='CCM',program_status='ACTIVE',patient__in=patients).count()
            return ccm_enrolled_patients
        except Exception as e:
            return result

    def get_inactive_patients_count(self, obj):
        result = 0
        try:
            patients = Patient.objects.filter(hospital=obj.hospital, caremanager_obj=obj)
            ccm_declined_patient = ProgramInformation.objects.filter(program_type__program_name='CCM',program_status='DECLINED',patient__in=patients).count()
            # care_manager_hopital_branch = obj.hospital.hospital_branch.filter(care_manager=obj)
            # patients = Patient.objects.filter(hospital=obj.hospital, caremanager__in=care_manager_hopital_branch)
            # ccm_declined_patient = ProgramInformation.objects.filter(program_type__program_name='CCM', program_status='DECLINED', patient__in=patients).count()
            return ccm_declined_patient
        except Exception as e:
            return result

    def get_not_reachable_patients_count(self, obj):
        result = 0
        try:
            patients = Patient.objects.filter(hospital=obj.hospital, caremanager_obj=obj)
            not_reachable_patient = ProgramInformation.objects.filter(program_type__program_name='CCM',program_status='NOTREACHABLE',patient__in=patients).count()

            # outreach_not_reachable_patient = PatientOutreach.objects.filter(resolution_action='NOT-REACHABLE', contact_type='TELEPHONE-CALL',care_manager=obj).count()
            
            # care_manager_hopital_branch = obj.hospital.hospital_branch.filter(care_manager=obj)
            # patients = Patient.objects.filter(hospital=obj.hospital, caremanager__in=care_manager_hopital_branch)
            # outreach_not_reachable_patient = PatientOutreach.objects.filter(resolution_action='NOT-REACHABLE', contact_type='PHONE',patient__in=patients).count()
            return not_reachable_patient
        except Exception as e:
            return result


class CareManagerDashboardDetailSerializer(serializers.Serializer):
    tasks = serializers.SerializerMethodField()
    patients = serializers.SerializerMethodField()
    enrolled_patients = serializers.SerializerMethodField()

    class Meta:
        fields = ("tasks", "patients", "enrolled_patients",)

    def get_tasks(self, obj):
        result = []
        try:
            # today = datetime.datetime.now().date()
            # tasks = Task.objects.filter(care_manager=obj, task_date=today)
            # goals = Goal.objects.filter(goal_date__date=today)
            # outreaches = PatientOutreach.objects.filter(schedule_follow_up_date=today)
            # combined_queryset = list(chain(tasks, goals, outreaches))
            # overdue_tasks = Task.objects.filter(care_manager=obj, task_date__lt=today)
            # overdue_goals = Goal.objects.filter(goal_date__date__lt=today)
            # overdue_outreaches = PatientOutreach.objects.filter(schedule_follow_up_date__lt=today)
            # overdue_combined_queryset = list(chain(overdue_tasks, overdue_goals, overdue_outreaches))
            # print(combined_queryset)
            # result = len(build_task_data(combined_queryset)) + len(build_task_data(overdue_combined_queryset))
            # return result


            tasks = Task.objects.filter(care_manager=obj)
            outreaches = PatientOutreach.objects.filter(care_manager=obj)
            combined_queryset = list(chain(tasks, outreaches))
            result = len(build_task_data(combined_queryset))
            return result
        except Exception as e:
            print(e)
            return result

    # def get_tasks(self, obj):
    #     result = 0
    #     try:
    #         get_hospital = obj.hospital
    #         pts = Patient.objects.filter(hospital=get_hospital).values_list('pk', flat=True)
    #         result = Task.objects.filter(patient__in=pts).count()
    #         return result
    #     except Exception as e:
    #         return result


    def get_patients(self, obj):
        result = 0
        try:
            patients = Patient.objects.filter(hospital=obj.hospital, caremanager_obj=obj).count()
            # care_manager_hopital_branch = obj.hospital.hospital_branch.filter(care_manager=obj)
            # patients = Patient.objects.filter(hospital=obj.hospital, caremanager__in=care_manager_hopital_branch).count()
            return patients
        except Exception as e:
            return result

    def get_enrolled_patients(self, obj):
        result = 0
        try:
            patients = Patient.objects.filter(hospital=obj.hospital, caremanager_obj=obj)
            ccm_enrolled_patients = ProgramInformation.objects.filter(program_type__program_name='CCM',program_status='ACTIVE',patient__in=patients).count()
            # care_manager_hopital_branch = obj.hospital.hospital_branch.filter(care_manager=obj)
            # patients = Patient.objects.filter(hospital=obj.hospital, caremanager__in=care_manager_hopital_branch)
            # ccm_enrolled_patients = ProgramInformation.objects.filter(program_type__program_name='CCM',program_status='ACTIVE',patient__in=patients).count()
            return ccm_enrolled_patients
        except Exception as e:
            return result


class PatientKeyStatSerializer(serializers.ModelSerializer):
    systolic = serializers.SerializerMethodField()
    blood_sugar = serializers.SerializerMethodField()
    pulse_rate = serializers.SerializerMethodField()
    weight = serializers.SerializerMethodField()
    total_cholesterol = serializers.SerializerMethodField()
    hbaic = serializers.SerializerMethodField()
    date_joined = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            "weight",
            "systolic",
            "blood_sugar",
            "pulse_rate",
            "total_cholesterol",
            "hbaic",
            "date_joined",
        ]

    def get_weight(self, obj):
        data = {}
        bmi_obj = BMI.objects.filter(patient=obj).last()
        if bmi_obj:
            data["Weight"] = bmi_obj.weight
            data["unit"] = bmi_obj.unit
            return data
        return data

    def get_systolic(self, obj):
        data = {}
        bp = BloodPressure.objects.filter(patient=obj).last()
        if bp:
            data["Sys"] = bp.systolic
            data["unit"] = "mmHg"
            return data
        return data

    def get_blood_sugar(self, obj):
        data = {}
        bg = BloodGlucose.objects.filter(patient=obj).last()
        if bg:
            data["Blood Glucose"] = bg.blood_sugar
            return data
        return data

    def get_pulse_rate(self, obj):
        data = {}
        po = PulseOx.objects.filter(patient=obj).last()
        if po:
            data["PulseOX"] = po.pulse_rate
            return data
        return data

    def get_total_cholesterol(self, obj):
        data = {}
        chl_obj = Cholesterol.objects.filter(patient=obj).last()
        if chl_obj:
            data["Cholesterol"] = chl_obj.total_cholesterol
            return chl_obj.total_cholesterol
        return data

    def get_hbaic(self, obj):
        data = {}
        hbc = HBA1C.objects.filter(patient=obj).last()
        if hbc:
            data["HbA1C"] = hbc.hbaic
            return data
        return data

    def get_date_joined(self, obj):
        return obj.created_at


# class PatientTreatmentSerializer(serializers.ModelSerializer):
#     total_time = serializers.SerializerMethodField()
#     remaining_days = serializers.SerializerMethodField()

#     class Meta:
#         model = Patient
#         fields = ['created_at', 'total_time', 'remaining_days']

#     def get_total_time(self, obj):
#         return "22 min"

#     def get_remaining_days(self, obj):
#         today_date = datetime.datetime.now()
#         current_month_days = calendar.monthrange(today_date.year, today_date.month)[1]
#         remaining_days = current_month_days - today_date.day
#         return remaining_days


class PatientTreatmentSerializer(serializers.ModelSerializer):
    total_time = serializers.SerializerMethodField()
    remaining_days = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    session_total_time = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            "created_at",
            "name",
            "total_time",
            "remaining_days",
            "session_total_time",
        ]

    def get_name(self, obj):
        return obj.user.email

    def get_session_total_time(self, obj):
        p_session = PatientSession.objects.filter(patient=obj)
        total_session_duration = sum([i.duration.seconds for i in p_session])
        total_time = str(datetime.timedelta(seconds=total_session_duration))
        return total_time

    def get_total_time(self, obj, format=None):
        result_sum = 0
        try:
            vcall = VitalCallLog.objects.filter(patient=obj)
            mcall = MedicalConditionCallLog.objects.filter(patient=obj)
            acall = AssessmentCallLog.objects.filter(patient=obj)
            awvcall = AnnualWellnessVisitCallLog.objects.filter(patient=obj)
            smpcall = SelfManagementPlanCallLog.objects.filter(patient=obj)

            total_vcall_duration = sum([i.call_duration.seconds for i in vcall])
            total_mcall_duration = sum([i.call_duration.seconds for i in mcall])
            total_acall_duration = sum([i.call_duration.seconds for i in acall])
            total_awvcall_duration = sum([i.call_duration.seconds for i in awvcall])
            total_smpcall_duration = sum([i.call_duration.seconds for i in smpcall])
            total_call_duration = (
                total_vcall_duration
                + total_mcall_duration
                + total_acall_duration
                + total_awvcall_duration
                + total_smpcall_duration
            )
            time = str(datetime.timedelta(seconds=total_call_duration))
            return time

        except Exception as e:
            return result_sum

    def get_remaining_days(self, obj):
        today_date = datetime.datetime.now()
        current_month_days = calendar.monthrange(today_date.year, today_date.month)[1]
        remaining_days = current_month_days - today_date.day
        return remaining_days


class AnnualWellnessVisitCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnualWellnessVist
        fields = [
            "id",
            "patient",
            "services_and_Screening_name",
            "date_of_last_services",
            "annual_wellness_status",
            "who",
            "often",
            "next_schedule_date",
            "need",
            "notes",
            "completed_by_date",
        ]


class AnnualWellnessVisitSerializer(serializers.ModelSerializer):
    services_and_Screening_name = serializers.SerializerMethodField()
    annual_wellness_status = serializers.CharField(
        source="get_annual_wellness_status_display"
    )
    who = serializers.SerializerMethodField()
    often = serializers.SerializerMethodField()

    class Meta:
        model = AnnualWellnessVist
        fields = [
            "id",
            "patient",
            "services_and_Screening_name",
            "date_of_last_services",
            "annual_wellness_status",
            "notes",
            "who",
            "often",
            "next_schedule_date",
            "need",
            "completed_by_date"
        ]

    def get_services_and_Screening_name(self, obj):
        if obj.services_and_Screening_name:
            return obj.services_and_Screening_name.name
        else:
            return None

    def get_who(self, obj):
        if obj.who:
            ser = obj.who
            return ser
        else:
            return None

    def get_often(self, obj):
        if obj.often:
            ser = obj.often
            return ser
        else:
            return None


class GetappointmentsProviderCountSerializer(serializers.Serializer):
    appointments_count = serializers.SerializerMethodField()
    assigned_provider_count = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ("appointments_count", "assigned_provider_count")

    def get_appointments_count(self, obj):
        patient_id = self.context.get("pk")
        appointments_count = Appointment.objects.filter(patient=patient_id).count()
        return appointments_count

    def get_assigned_provider_count(self, obj):
        patient_id = self.context.get("pk")
        assigned_provider_count = PatientProviderMapping.objects.filter(
            patient=patient_id
        ).count()
        return assigned_provider_count


class GetPatientMedicationsSerializer(serializers.Serializer):
    medications = serializers.SerializerMethodField()

    class Meta:
        fields = "medications"

    def get_medications(self, obj):
        all_treatments = [
            treatment.medications for treatment in obj.first().patient_treatment.all()
        ]

        return all_treatments


class BMISerializer(serializers.ModelSerializer):
    class Meta:
        model = BMI
        fields = "__all__"


class BloodPressureSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodPressure
        fields = "__all__"


class BloodGlucoseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodGlucose
        fields = "__all__"


class PulseOxSerializer(serializers.ModelSerializer):
    class Meta:
        model = PulseOx
        fields = "__all__"


class HBA1CSerializer(serializers.ModelSerializer):
    class Meta:
        model = HBA1C
        fields = "__all__"


class CholesterolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cholesterol
        fields = "__all__"


class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = "__all__"


class PatientContactDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientContactDetails
        fields = "__all__"


class PatientContactDetailsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientContactDetails
        fields = "__all__"

    def create(self, validated_data):
        communication = validated_data.get("communication", None)
        # pop manytomany field
        validated_data.pop("communication")
        patient = validated_data.pop("patient")
        pcd, updated = PatientContactDetails.objects.update_or_create(
            patient=patient, defaults=validated_data
        )
        pcd.communication.set(communication)
        return pcd


class StepsToAchieveGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = StepsToAchieveGoal
        fields = "__all__"


class GoalChallengesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalChallenges
        fields = "__all__"


class AssistanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assistance
        fields = "__all__"


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ["pk", "name"]


class GoalsTaskSerializer(serializers.ModelSerializer):
    goal_tasks = serializers.SerializerMethodField()
    steps_to_achieve_goal = StepsToAchieveGoalSerializer(many=True)
    challenge_goal = GoalChallengesSerializer(many=True)
    assistance_goal = AssistanceSerializer(many=True)

    class Meta:
        model = Goal
        fields = [
            "pk",
            "name",
            "goal_date",
            "goal_status",
            "notes",
            "chronic_condition",
            "patient",
            "patient_refused",
            "goal_tasks",
            "steps_to_achieve_goal",
            "challenge_goal",
            "assistance_goal",
        ]

    def get_goal_tasks(self, obj):
        goaltask = Intervention.objects.filter(goal=obj)
        ser = InterventionSerializer(goaltask, many=True)
        return ser.data


class GoalCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    goal_date = serializers.DateField()
    goal_status = serializers.CharField(max_length=50)
    notes = serializers.CharField(max_length=255, required=False)
    patient_refused = serializers.BooleanField()
    patient = serializers.CharField()
    chronic_condition = serializers.CharField(max_length=255, required=False)

    steps_to_achieve_goals = StepsToAchieveGoalSerializer(many=True)
    goal_challenges = GoalChallengesSerializer(many=True)
    goal_assistance = AssistanceSerializer(many=True)

    # Convert ID of patient to object of Patient
    def validate_patient(self, patient):
        patient_obj = None
        if patient:
            patient_obj = Patient.objects.filter(pk=patient).last()
        return patient_obj

    # Convert ID of Chronic Condition to object
    def validate_chronic_condition(self, chronic_condition):
        chronic_obj = None
        if chronic_condition:
            chronic_obj = ChronicCondition.objects.filter(pk=chronic_condition).last()
        return chronic_obj

    def save(self):
        # Pop the unwanted data from validated data
        goal_steps_list = self.validated_data.pop("steps_to_achieve_goals")
        goal_challenge_list = self.validated_data.pop("goal_challenges")
        goal_assistance_list = self.validated_data.pop("goal_assistance")

        # Create Goal
        goal_obj = Goal.objects.create(**self.validated_data)

        if goal_steps_list:
            for goal_step_data in goal_steps_list:
                ser = StepsToAchieveGoalSerializer(data=goal_step_data)
                if ser.is_valid():
                    # Store the above goal object in Model
                    ser.save(goal=goal_obj)
                else:
                    print(ser.errors)

        if goal_challenge_list:
            for goal_challenge_data in goal_challenge_list:
                ser_challenge = GoalChallengesSerializer(data=goal_challenge_data)
                if ser_challenge.is_valid():
                    # Store the above goal object in Model
                    ser_challenge.save(goal=goal_obj)
                else:
                    print(ser_challenge.errors)
        if goal_assistance_list:
            for goal_assistance_data in goal_assistance_list:
                ser_assistance = AssistanceSerializer(data=goal_assistance_data)
                if ser_assistance.is_valid():
                    # Store the above goal object in Model
                    ser_assistance.save(goal=goal_obj)
                else:
                    print(ser_assistance.errors)
        return goal_obj


# class TaskSerializer(serializers.ModelSerializer):
#     name = serializers.SerializerMethodField()
#     task_type = serializers.SerializerMethodField()
#     task_due_date = serializers.SerializerMethodField()
#     time_spent = serializers.SerializerMethodField()
#     score = serializers.SerializerMethodField()
#     status = serializers.SerializerMethodField()
#     task_goal_intervention_id = serializers.SerializerMethodField()
#     intervention = InterventionSerializer(required=False)
#     goal = serializers.SerializerMethodField()
#     # intervention = serializers.SerializerMethodField()
#     # goal = serializers.SerializerMethodField()
#
#
#     class Meta:
#         model = Task
#         fields = ["task_goal_intervention_id", "notes", "goal", "intervention", "patient", "care_manager", "task_date",
#                   "task_status", "name", "task_type", "task_due_date", "time_spent", "score", "status", "goal"]
#
#     def get_task_goal_intervention_id(self, obj):
#         if obj.goal:
#             return obj.goal.id
#         elif obj.intervention:
#             return obj.intervention.id
#         else:
#             return None
#
#     def get_name(self, obj):
#         # As when task is added solely FK of goal is also provided
#         if obj.goal and obj.is_self_task == False:
#             return obj.goal.name
#         elif obj.intervention:
#             return obj.intervention.name
#         elif obj.is_self_task:
#             return obj.name
#         else:
#             return None
#
#     def get_task_type(self, obj):
#         if obj.goal:
#             return "Goal"
#         elif obj.intervention:
#             return "Task"
#         else:
#             return None
#
#     def get_task_due_date(self, obj):
#         if obj.goal:
#             return obj.goal.goal_date
#         elif obj.intervention:
#             return obj.intervention.date
#         else:
#             return None
#
#     def get_time_spent(self, obj):
#         return 20
#
#     def get_score(self, obj):
#         return None
#
#     def get_status(self, obj):
#         if obj.goal:
#             return obj.goal.goal_status
#         elif obj.intervention:
#             return obj.intervention.status
#         else:
#             return None
#
#     def get_goal(self, obj):
#         patient_goals = obj.goal
#         if patient_goals:
#             result = {}
#             result["name"] = patient_goals.name
#             result["goal_date"] = patient_goals.goal_date
#             result["chronic_condition"] = patient_goals.chronic_condition.disease_name
#             result["notes"] = patient_goals.notes
#             result["goal_status"] = patient_goals.goal_status
#
#
#             steps_to_achieve_goals = patient_goals.steps_to_achieve_goal.all()
#             steps_to_achieve_goals_list = []
#             if steps_to_achieve_goals:
#                 for steps_to_achieve_goal in steps_to_achieve_goals:
#                     dict = {}
#                     dict["goal_plan"]= steps_to_achieve_goal.goal_plan
#                     dict["score"]= steps_to_achieve_goal.score
#                     steps_to_achieve_goals_list.append(dict)
#                 result["steps_to_achieve_goals"] = steps_to_achieve_goals_list
#                 # return list
#             else:
#                 steps_to_achieve_goals_list.append({'goal_plan':None, 'score':None})
#                 result["steps_to_achieve_goals"] = steps_to_achieve_goals_list
#
#
#             challenge_goals = patient_goals.challenge_goal.all()
#             challenge_goals_list = []
#             if challenge_goals:
#                 for challenge_goal in  challenge_goals:
#                     dict = {}
#                     dict["challenges"]= challenge_goal.challenges
#                     dict["score"]= challenge_goal.score
#                     challenge_goals_list.append(dict)
#                 result["challenge_goals"] = challenge_goals_list
#             else:
#                 challenge_goals_list.append({'challenges':None, 'score':None})
#                 result["challenge_goals"] = challenge_goals_list
#
#
#             assistance_goals = patient_goals.assistance_goal.all()
#             assistance_goals_list = []
#             if assistance_goals:
#                 for assistance_goal in  assistance_goals:
#                     dict = {}
#                     dict["support_type"]= assistance_goal.support_type
#                     dict["score"]= assistance_goal.score
#                     assistance_goals_list.append(dict)
#                 result["assistance_goals"] = assistance_goals_list
#             else:
#                 assistance_goals_list.append({'support_type':None, 'score':None})
#                 result["assistance_goals"] = assistance_goals_list
#
#             return result
#         else:
#             return None


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class MedicationNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationNotes
        fields = "__all__"


class CreatepatientforcaremanagerSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField(required=False)
    email = serializers.SerializerMethodField()
    # caremanager = serializers.SerializerMethodField()
    caremanager_obj = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = (
            "id",
            "title",
            "first_name",
            "middle_name",
            "last_name",
            "dob",
            "gender",
            "profile_pic",
            "email",
            # "caremanager",
            "caremanager_obj",
        )

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_profile_pic(self, obj):
        if obj.user.profile_pic:
            return settings.BACKEND_URL + obj.user.profile_pic.url
        else:
            return None

    def get_email(self, obj):
        return obj.user.email

    # def get_caremanager(self, obj):
    #     if obj.caremanager:
    #         return (
    #             str(obj.caremanager.care_manager.user.first_name)
    #             + " "
    #             + str(obj.caremanager.care_manager.user.last_name)
    #         )
    #     else:
    #         return None

    def get_caremanager_obj(self, obj):
        if obj.caremanager_obj:
            return (
                obj.caremanager_obj.user.first_name
                + " "
                + obj.caremanager_obj.user.last_name
            )
        else:
            return None


class PatientCallLogSerializer(serializers.ModelSerializer):
    call_status = serializers.SerializerMethodField()
    call_type = serializers.SerializerMethodField()

    class Meta:
        model = PatientCallLog
        # fields = "__all__"
        fields = [
            "agenda",
            "recording",
            "call_meet_link",
            "patient",
            "care_manager",
            "call_start_datetime",
            "call_end_datetime",
            "call_duration",
            "call_status",
            "call_type",
        ]

    def get_call_status(self, obj):
        return obj.get_call_status_display()

    def get_call_type(self, obj):
        return obj.get_call_type_display()


class PatientCallLogEndSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientCallLog
        fields = ["call_meet_link", "patient", "care_manager"]


class PatientVitalGlobalSearchSerializer(serializers.ModelSerializer):
    bmi = serializers.SerializerMethodField()
    bloodpressure = serializers.SerializerMethodField()
    bloodglucose = serializers.SerializerMethodField()
    cholesterol = serializers.SerializerMethodField()
    pulse_ox = serializers.SerializerMethodField()
    hba1c = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            "bmi",
            "bloodpressure",
            "bloodglucose",
            "cholesterol",
            "pulse_ox",
            "hba1c",
        ]

    def get_bmi(self, obj):
        from_date = self.context["from_date"]
        to_date = self.context["to_date"]
        bmi_data = []
        bmis = obj.patient_bmi.filter(created_at__range=[from_date, to_date])
        if bmis:
            for bmi in bmis:
                data = {}
                data["weight"] = bmi.weight
                data["height"] = bmi.height
                data["bmi_score"] = bmi.bmi_score
                bmi_data.append(data)
            return bmi_data
        return bmi_data.append(0)

    def get_bloodpressure(self, obj):
        from_date = self.context["from_date"]
        to_date = self.context["to_date"]
        bloodpressure_data = []
        bloodpressure_obj = obj.patient_blood_pressure.filter(
            created_at__range=[from_date, to_date]
        )
        if bloodpressure_obj:
            for bloodpressure in bloodpressure_obj:
                data = {}
                data["pulse"] = bloodpressure.pulse
                data["systolic"] = bloodpressure.systolic
                data["diastolic"] = bloodpressure.diastolic
                bloodpressure_data.append(data)
            return bloodpressure_data
        else:
            return bloodpressure_data.append(0)

    def get_bloodglucose(self, obj):
        from_date = self.context["from_date"]
        to_date = self.context["to_date"]
        bloodglucose_data = []
        bloodglucose = obj.patient_blood_glucose.filter(
            created_at__range=[from_date, to_date]
        )
        if bloodglucose:
            for glucose in bloodglucose:
                data = {}
                data["blood_sugar"] = glucose.blood_sugar
                data["test_type"] = glucose.test_type
                bloodglucose_data.append(data)
            return bloodglucose_data
        return bloodglucose_data.append(0)

    def get_cholesterol(self, obj):
        from_date = self.context["from_date"]
        to_date = self.context["to_date"]
        cholesterol_data = []
        cholesterol_obj = obj.patient_cholesterol.filter(
            created_at__range=[from_date, to_date]
        )
        if cholesterol_obj:
            for cholesterol in cholesterol_obj:
                data = {}
                data["total_cholesterol"] = cholesterol.total_cholesterol
                data["triglycerides"] = cholesterol.triglycerides
                data["hdl"] = cholesterol.hdl
                data["ldl"] = cholesterol.ldl
                cholesterol_data.append(data)
            return cholesterol_data
        else:
            return cholesterol_data.append(0)

    def get_pulse_ox(self, obj):
        from_date = self.context["from_date"]
        to_date = self.context["to_date"]
        pulse_ox_data = []
        pulse_ox = obj.patient_pulseOx.filter(created_at__range=[from_date, to_date])
        if pulse_ox:
            for pulse in pulse_ox:
                data = {}
                data["spo2"] = pulse.spo2
                data["pulse_rate"] = pulse.pulse_rate
                pulse_ox_data.append(data)
            return pulse_ox_data
        else:
            return pulse_ox_data.append(0)

    def get_hba1c(self, obj):
        from_date = self.context["from_date"]
        to_date = self.context["to_date"]
        hba1c_data = []
        hba1c = obj.patient_hba1c.filter(created_at__range=[from_date, to_date])
        if hba1c:
            for hba in hba1c:
                data = {}
                data["hbaic"] = hba.hbaic
                hba1c_data.append(data)
            return hba1c_data
        else:
            return hba1c_data.append(0)


class PatientMonthlyReportSerializer(serializers.ModelSerializer):
    personal_information = serializers.SerializerMethodField()
    medications = serializers.SerializerMethodField()
    conditions_monitored = serializers.SerializerMethodField()
    conditions_assessments = serializers.SerializerMethodField()
    goals = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()

    class Meta:
        model = Patient

        fields = [
            "personal_information",
            "medications",
            "conditions_monitored",
            "conditions_assessments",
            "goals",
            "details",
        ]

    def get_personal_information(self, obj):
        request = self.context.get("request")
        if request.query_params.get("personal_information"):
            personal_info = get_patient_personal_info(obj)
            return personal_info
        else:
            return None

    def get_goals(self, obj):
        request = self.context.get("request")
        month_first_date = datetime.datetime.today().replace(
            day=1
        ) - datetime.timedelta(days=1)
        current_date = datetime.datetime.now() + datetime.timedelta(days=1)
        if request.query_params.get("self_management_goals"):

            list = []
            for goal in obj.patient_goal.filter(
                created_at__range=[month_first_date, current_date]
            ):
                dict = {}
                dict["goal_name"] = goal.name
                dict["goal_date"] = goal.goal_date.date()
                dict["goal_status"] = goal.goal_status
                list.append(dict)
            return list

        else:
            return None

    def get_medications(self, obj):
        request = self.context.get("request")
        month_first_date = datetime.datetime.today().replace(
            day=1
        ) - datetime.timedelta(days=1)
        current_date = datetime.datetime.now() + datetime.timedelta(days=1)

        if request.query_params.get("medications"):
            data_li = []
            medication_id = obj.patient_medication.filter(
                created_at__range=[month_first_date, current_date]
            )
            for name in medication_id:
                data = {}
                data["id"] = name.id
                data["name"] = name.medication_name
                data["dose"] = name.dose
                data["type"] = name.type
                data["frequency"] = name.frequency
                data["prescriber"] = name.prescriber
                data["status"] = name.is_active
                data_li.append(data)
            return data_li

        else:
            return None

    # def get_conditions_monitored(self, obj):
    #     request = self.context.get("request")
    #     month_first_date = datetime.datetime.today().replace(day=1) - datetime.timedelta(days=1)
    #     current_date = datetime.datetime.now() + datetime.timedelta(days=1)

    #     if request.query_params.get("conditions_monitored"):
    #         data_li = []
    #         patient_bp = obj.patient_blood_pressure.filter(created_at__range=[month_first_date, current_date])
    #         patient_hba1c = obj.patient_hba1c.filter(created_at__range=[month_first_date, current_date])
    #         patient_cholesterol = obj.patient_cholesterol.filter(created_at__range=[month_first_date, current_date])
    #         patient_pulseox = obj.patient_pulseOx.filter(created_at__range=[month_first_date, current_date])
    #         patient_blood_glucose = obj.patient_blood_glucose.filter(created_at__range=[month_first_date, current_date])
    #         for name in patient_bp:
    #             data = {}
    #             data['blood_pressure'] = name.notes
    #             data_li.append(data)

    #         for name in patient_hba1c:
    #             data = {}
    #             data['hba1c'] = name.notes
    #             data_li.append(data)

    #         for name in patient_cholesterol:
    #             data = {}
    #             data['cholesterol'] = name.notes
    #             data_li.append(data)

    #         for name in patient_pulseox:
    #             data = {}
    #             data['pulseOx'] = name.notes
    #             data_li.append(data)

    #         for name in patient_blood_glucose:
    #             data = {}
    #             data['blood_glucose'] = name.notes
    #             data_li.append(data)
    #         return data_li

    def get_conditions_monitored(self, obj):
        request = self.context.get("request")
        month_first_date = datetime.datetime.today().replace(
            day=1
        ) - datetime.timedelta(days=1)
        current_date = datetime.datetime.now() + datetime.timedelta(days=1)

        if request.query_params.get("conditions_monitored"):
            result = {}
            # data_li = []
            patient_bp = obj.patient_blood_pressure.filter(
                created_at__range=[month_first_date, current_date]
            )
            patient_hba1c = obj.patient_hba1c.filter(
                created_at__range=[month_first_date, current_date]
            )
            patient_cholesterol = obj.patient_cholesterol.filter(
                created_at__range=[month_first_date, current_date]
            )
            patient_pulseox = obj.patient_pulseOx.filter(
                created_at__range=[month_first_date, current_date]
            )
            patient_blood_glucose = obj.patient_blood_glucose.filter(
                created_at__range=[month_first_date, current_date]
            )
            bloodpressure_data = []
            try:
                for bloodpressure in patient_bp:
                    data = {}
                    data["pulse"] = bloodpressure.pulse
                    data["systolic"] = bloodpressure.systolic
                    data["diastolic"] = bloodpressure.diastolic
                    bloodpressure_data.append(data)
                    result["bloodpressure"] = bloodpressure_data
            except Exception as e:
                return bloodpressure_data

            patient_hba1c_list = []
            try:
                for name in patient_hba1c:
                    data = {}
                    data["hba1c"] = name.hbaic
                    patient_hba1c_list.append(data)
                    result["hba1c"] = patient_hba1c_list
            except Exception as e:
                return patient_hba1c_list

            cholesterol_data = []
            try:
                for cholesterol in patient_cholesterol:
                    data = {}
                    data["total_cholesterol"] = cholesterol.total_cholesterol
                    data["triglycerides"] = cholesterol.triglycerides
                    data["hdl"] = cholesterol.hdl
                    data["ldl"] = cholesterol.ldl
                    cholesterol_data.append(data)
                    result["cholesterol"] = cholesterol_data
            except Exception as e:
                return cholesterol_data

            patient_pulseox_list = []
            try:
                for name in patient_pulseox:
                    data = {}
                    data["spo2"] = name.spo2
                    data["pulse_rate"] = name.pulse_rate
                    patient_pulseox_list.append(data)
                    result["pulseox"] = patient_pulseox_list
            except Exception as e:
                return patient_pulseox_list

            bloodglucose_data = []
            try:
                for glucose in patient_blood_glucose:
                    data = {}
                    data["blood_sugar"] = glucose.blood_sugar
                    data["test_type"] = glucose.test_type
                    bloodglucose_data.append(data)
                    result["bloodglucose"] = bloodglucose_data
            except Exception as e:
                return bloodglucose_data

            return result
        else:
            return None

    def get_conditions_assessments(self, obj):
        request = self.context.get("request")
        month_first_date = datetime.datetime.today().replace(
            day=1
        ) - datetime.timedelta(days=1)
        current_date = datetime.datetime.now() + datetime.timedelta(days=1)
        if request.query_params.get("assessments"):
            data_li = []
            patient_assessment = obj.patient_assessment.filter(
                created_at__range=[month_first_date, current_date]
            )
            for name in patient_assessment:
                data = {}
                data["id"] = name.id
                data["date"] = name.start_date
                data["score"] = name.score
                data["assessment_status"] = name.assessment_status

                data_li.append(data)
            return data_li

        else:
            return None

    def get_details(self, obj):
        detail_list = []
        request = self.context.get("request")
        if request.query_params.get("details"):
            if obj.patient_patientprovidermapping.first():
                provider_name = (
                    obj.patient_patientprovidermapping.first().primary_provider.user.first_name
                )
                return provider_name
            else:
                return detail_list
        else:
            return None

    # def get_care_manager_name(self, obj):
    #     return None

    # def get_provider_name(self, obj):
    #     if obj.patient_patientprovidermapping.first():
    #         return obj.patient_patientprovidermapping.first().primary_provider.user.first_name
    #     else:
    #         return None
    # def get_due_date(self, obj):
    #     return "2022-11-23"


class PatientSummarySerializer(serializers.ModelSerializer):
    personal_information = serializers.SerializerMethodField()
    medication = serializers.SerializerMethodField()
    vitals = serializers.SerializerMethodField()
    self_management_goals = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    assessment = serializers.SerializerMethodField()
    care_gap = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            "personal_information",
            "medication",
            "vitals",
            "self_management_goals",
            "details",
            "assessment",
            "care_gap"
        ]

    def get_personal_information(self, obj):
        request = self.context.get("request")
        if request.query_params.get("personal_information"):
            personal_info = get_patient_personal_info(obj)
            return personal_info
        else:
            return None

    def get_medication(self, obj):
        request = self.context.get("request")
        if request.query_params.get("medication"):
            month_first_date = datetime.datetime.today().replace(
                day=1
            ) - datetime.timedelta(days=1)
            current_date = datetime.datetime.now() + datetime.timedelta(days=1)
            medication_list = []
            medication = obj.patient_medication.filter(
                created_at__range=[month_first_date, current_date]
            )
            if medication:
                for name in medication:
                    data = {}
                    data["id"] = name.id
                    data["name"] = name.medication_name
                    data["dose"] = name.dose
                    data["type"] = name.midication_status
                    data["frequency"] = name.frequency
                    data["prescriber"] = name.prescriber
                    data["status"] = name.is_active
                    data["date"] = name.created_at.date()
                    medication_list.append(data)
                return medication_list
            else:
                return [
                    {
                        "id": None,
                        "name": None,
                        "dose": None,
                        "type": None,
                        "frequency": None,
                        "prescriber": None,
                        "status": None,
                        "date": None,
                    }
                ]
        else:
            return None

    def get_vitals(self, obj):
        request = self.context.get("request")
        month_first_date = datetime.datetime.today().replace(
            day=1
        ) - datetime.timedelta(days=1)
        current_date = datetime.datetime.now() + datetime.timedelta(days=1)
        result = {}
        if request.query_params.get("vitals"):
            bmi_data = []
            bmi = obj.patient_bmi.all().last()
            if bmi:
                data = {}
                data["weight"] = bmi.weight
                data["height"] = bmi.height
                data["height_ft"] = bmi.height_ft
                data["height_inch"] = bmi.height_inch                
                data["bmi_score"] = bmi.bmi_score 
                data["date"] = bmi.date                
                bmi_data.append(data)
                result["bmi"] = bmi_data
            else:
                bmi_data.append(
                    {
                        "weight": None,
                        "height": None,
                        "height_inch": None,
                        "bmi_score": None,
                        "date":None
                    }
                )
                result["bmi"] = bmi_data

            bloodpressure_data = []
            bloodpressure = obj.patient_blood_pressure.all().last()
            if bloodpressure:
                data = {}
                data["pulse"] = bloodpressure.pulse
                data["systolic"] = bloodpressure.systolic
                data["diastolic"] = bloodpressure.diastolic
                data["date"] = bloodpressure.date
                bloodpressure_data.append(data)
                result["bloodpressure"] = bloodpressure_data
            else:
                bloodpressure_data.append(
                    {"pulse": None, "systolic": None, "diastolic": None, "date": None}
                )
                result["bloodpressure"] = bloodpressure_data

            cholesterol_data = []
            cholesterol = obj.patient_cholesterol.all().last()
            if cholesterol:
                data = {}
                data["total_cholesterol"] = cholesterol.total_cholesterol
                data["triglycerides"] = cholesterol.triglycerides
                data["hdl"] = cholesterol.hdl
                data["ldl"] = cholesterol.ldl
                data["date"] = cholesterol.date
                cholesterol_data.append(data)
                result["cholesterol"] = cholesterol_data
            else:
                cholesterol_data.append(
                    {
                        "total_cholesterol": None,
                        "triglycerides": None,
                        "hdl": None,
                        "ldl": None,
                        "date": None
                    }
                )
                result["cholesterol"] = cholesterol_data

            bloodglucose_data = []
            glucose = obj.patient_blood_glucose.all().last()
            if glucose:
                data = {}
                data["blood_sugar"] = glucose.blood_sugar
                data["test_type"] = glucose.test_type
                data["date"] = glucose.date
                bloodglucose_data.append(data)
                result["bloodglucose"] = bloodglucose_data
            else:
                bloodglucose_data.append({"blood_sugar": None, "test_type": None, "date":None})
                result["bloodglucose"] = bloodglucose_data

        
        
            pulse_ox_data = []
            pulseox = obj.patient_pulseOx.all().last()
            if pulseox:
                data = {}
                data["spo2"] = pulseox.spo2
                data["pulse_rate"] = pulseox.pulse_rate
                data["spo2_value"] = pulseox.spo2_value
                data["source_entry"] = pulseox.source_entry
                data["date"] = pulseox.date
                pulse_ox_data.append(data)
                result["pulseOx"] = pulse_ox_data
            else:
                pulse_ox_data.append({"spo2": None, "pulse_rate": None,"spo2_value":None,"source_entry":None,"date":None})
                result["pulseOx"] = pulse_ox_data
                
            hba1c_data = []
            hba1c = obj.patient_hba1c.all().last()
            if hba1c:
                data = {}
                data["hbaic"] = hba1c.hbaic
                data["source_entry"] = hba1c.source_entry
                data["date"] = hba1c.date
                hba1c_data.append(data)
                result["hba1c"] = hba1c_data
            else:
                hba1c_data.append({"hbaic": None, "source_entry": None, "date":None})
                result["hba1c"] = hba1c_data

            return result
        else:
            return None

    # def get_vitals(self, obj):
    #     request = self.context.get("request")
    #     month_first_date = datetime.datetime.today().replace(day=1) - datetime.timedelta(days=1)
    #     current_date = datetime.datetime.now() + datetime.timedelta(days=1)
    #     result = {}
    #     if request.query_params.get("vitals"):
    #         bmi_data = []
    #         bmis = obj.patient_bmi.filter(created_at__range=[month_first_date, current_date])
    #         if bmis:
    #             for bmi in bmis:
    #                 data = {}
    #                 data['weight'] = bmi.weight
    #                 data['height_ft'] = bmi.height_ft
    #                 data['height_inch'] = bmi.height_inch
    #                 bmi_data.append(data)
    #             result["bmi"] = bmi_data
    #         else:

    #             bmi_data.append({'weight':None, 'height_ft':None, 'height_inch':None})
    #             result["bmi"] = bmi_data

    #         bloodpressure_data = []
    #         bloodpressure_obj = obj.patient_blood_pressure.filter(created_at__range=[month_first_date, current_date])
    #         if bloodpressure_obj:
    #             for bloodpressure in bloodpressure_obj:
    #                 data = {}
    #                 data['pulse'] = bloodpressure.pulse
    #                 data['systolic'] = bloodpressure.systolic
    #                 data['diastolic'] = bloodpressure.diastolic
    #                 bloodpressure_data.append(data)

    #             result["bloodpressure"] = bloodpressure_data
    #         else:
    #             bloodpressure_data.append({'pulse':None, 'systolic':None, 'diastolic':None})
    #             result["bloodpressure"] = bloodpressure_data

    #         cholesterol_data = []
    #         cholesterol_obj = obj.patient_cholesterol.filter(created_at__range=[month_first_date, current_date])
    #         if cholesterol_obj:
    #             for cholesterol in cholesterol_obj:
    #                 data = {}
    #                 data['total_cholesterol'] = cholesterol.total_cholesterol
    #                 data['triglycerides'] = cholesterol.triglycerides
    #                 data['hdl'] = cholesterol.hdl
    #                 data['ldl'] = cholesterol.ldl
    #                 cholesterol_data.append(data)
    #             result["cholesterol"] = cholesterol_data
    #         else:
    #             cholesterol_data.append({'total_cholesterol':None, 'triglycerides':None, 'hdl':None, 'ldl':None})
    #             result["cholesterol"] = cholesterol_data

    #         bloodglucose_data = []
    #         bloodglucose = obj.patient_blood_glucose.filter(created_at__range=[month_first_date, current_date])
    #         if bloodglucose:
    #             for glucose in bloodglucose:
    #                 data = {}
    #                 data['blood_sugar'] = glucose.blood_sugar
    #                 data['test_type'] = glucose.test_type
    #                 bloodglucose_data.append(data)
    #             result["bloodglucose"] = bloodglucose_data
    #             return result
    #         else:
    #             bloodglucose_data.append({'blood_sugar':None, 'test_type':None})
    #             result["bloodglucose"] = bloodglucose_data
    #         return result
    #     else:
    #         return None

    def get_self_management_goals(self, obj):
        request = self.context.get("request")
        if request.query_params.get("self_management_goals"):
            month_first_date = datetime.datetime.today().replace(
                day=1
            ) - datetime.timedelta(days=1)
            current_date = datetime.datetime.now() + datetime.timedelta(days=1)
            goal_list = []
            obj = obj.patient_goal.filter(
                created_at__range=[month_first_date, current_date]
            )
            if obj:
                for goal in obj:
                    dict = {}
                    dict["goal_name"] = goal.name
                    dict["goal_date"] = goal.goal_date.date()
                    dict["goal_status"] = goal.get_goal_status_display()
                    goal_list.append(dict)
                return goal_list
            else:
                return [{"goal_name": None, "goal_date": None, "goal_status": None}]
        else:
            return None

    def get_details(self, obj):
        # detail_list = []
        request = self.context.get("request")
        if request.query_params.get("details"):
            if obj.patient_patientprovidermapping.first():
                provider_name = (
                    obj.patient_patientprovidermapping.first().primary_provider.user.first_name
                )
                return provider_name
            else:
                return [{"detail_list": None}]
        else:
            return None
    
    def get_assessment(self, obj):
        request = self.context.get("request")
        if request.query_params.get("assessments"):
            assessment = Assessment.objects.filter(patient=obj, is_active = True)
            if assessment:
                serializer = ListPatientAssessmentSerializer(assessment, many=True)
                assessment_data = serializer.data
            else:
                assessment_data = {
                    "assessment_name":None, 
                    "date":None, 
                    "score":None, 
                    "assessment_status":None, 
                    "time_spent":None, 
                    "severity":None 
                }
            return assessment_data
        
        
    def get_care_gap(self, obj):
        request = self.context.get("request")
        if request.query_params.get("care_gap"):
            month_first_date = datetime.datetime.today().replace(
                day=1
            ) - datetime.timedelta(days=1)
            current_date = datetime.datetime.now() + datetime.timedelta(days=1)
            awv_list = []            
            obj = obj.awv_patient.filter(created_at__date__range=[month_first_date, current_date])
            if obj:
                for awv in obj:
                    if awv.need==True or awv.date_of_last_services is not None or awv.completed_by_date is not None:
                        dict = {}
                        dict["services_and_Screening_name"] = awv.services_and_Screening_name.name
                        dict["date_of_last_services"] = awv.date_of_last_services  
                        dict["notes"] = awv.notes
                        dict["who"] = awv.who
                        dict["often"] = awv.often 
                        dict["next_schedule_date"] = awv.next_schedule_date    
                        dict["need"]= awv.need
                        dict["completed_by_date"] = awv.completed_by_date      
                        dict["annual_wellness_status"] = awv.get_annual_wellness_status_display()
                        awv_list.append(dict)
                return awv_list
            else:
                return [{"services_and_Screening_name": None, "date_of_last_services": None, "notes": None, "who": None, "often": None, "next_schedule_date": None, "need": None, "completed_by_date": None, "annual_wellness_status": None}]
        else:
            return None    


class CoordinationReportSerializer(serializers.ModelSerializer):
    personal_information = serializers.SerializerMethodField()
    medication = serializers.SerializerMethodField()
    allergies = serializers.SerializerMethodField()
    immunization = serializers.SerializerMethodField()
    labreport = serializers.SerializerMethodField()
    patientdocs = serializers.SerializerMethodField()
    problems = serializers.SerializerMethodField()
    procedures = serializers.SerializerMethodField()
    vitals = serializers.SerializerMethodField()
    self_management_goals = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    assessment = serializers.SerializerMethodField()
    caregap = serializers.SerializerMethodField()
    manual_log = serializers.SerializerMethodField()
    session_log = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            "personal_information",
            "medication",
            "allergies",
            "immunization",
            "labreport",
            "patientdocs",
            "problems",
            "procedures",
            "vitals",
            "self_management_goals",
            "details",
            "assessment",
            "caregap",
            "manual_log",
            "session_log",
        ]

    def get_personal_information(self, obj):
        if obj:
            personal_info = get_patient_personal_info(obj)
            return personal_info
        else:
            return None

    def get_medication(self, obj):
        request = self.context.get("request")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        if from_date and to_date:
            medication_list = []
            medication = obj.patient_medication.filter(
                created_at__date__range=[from_date, to_date]
            )
            if medication:
                for name in medication:
                    data = {}
                    data["id"] = name.id
                    data["name"] = name.medication_name
                    data["dose"] = name.dose
                    data["type"] = name.midication_status
                    data["frequency"] = name.frequency
                    data["prescriber"] = name.prescriber
                    data["status"] = name.is_active
                    data["date"] = name.created_at.date()
                    medication_list.append(data)
                return medication_list
            else:
                return [
                    {
                        "id": None,
                        "name": None,
                        "dose": None,
                        "type": None,
                        "frequency": None,
                        "prescriber": None,
                        "status": None,
                        "date": None,
                    }
                ]
        else:
            return None
    
    def get_allergies(self, obj):
        request = self.context.get("request")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        if from_date and to_date:
            allergies_list = []
            allergies = obj.patient_allergies.filter(
                created_at__date__range=[from_date, to_date]
            )
            if allergies:
                for allergy in allergies:
                    data = {}
                    data["id"] = allergy.id
                    data["name"] = allergy.name
                    data["description"] = allergy.description
                    data["file_field"] = None
                    data["source_entry"] = allergy.source_entry
                    data["date"] = allergy.created_at.date()
                    allergies_list.append(data)
                return allergies_list
            else:
                return [
                    {
                        "id": None,
                        "name": None,
                        "description": None,
                        "file_field": None,
                        "source_entry": None,
                        "date": None,
                    }
                ]
        else:
            return None
        
    def get_immunization(self, obj):
        request = self.context.get("request")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        if from_date and to_date:
            immunization_list = []
            immunizations = obj.patient_immunization.filter(
                created_at__date__range=[from_date, to_date]
            )
            if immunizations:
                for immunization in immunizations:
                    data = {}
                    data["id"] = immunization.id
                    data["name"] = immunization.name
                    data["description"] = immunization.description
                    data["file_field"] = None
                    data["physician_name"] = immunization.physician_name
                    data["source_entry"] = immunization.source_entry
                    data["date"] = immunization.created_at.date()
                    immunization_list.append(data)
                return immunization_list
            else:
                return [
                    {
                        "id": None,
                        "name": None,
                        "description": None,
                        "file_field": None,
                        "physician_name": None,
                        "source_entry": None,
                        "date": None,
                    }
                ]
        else:
            return None
        
    def get_labreport(self, obj):
        request = self.context.get("request")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        if from_date and to_date:
            labreport_list = []
            labreports = obj.patient_labreport.filter(
                created_at__date__range=[from_date, to_date]
            )
            if labreports:
                for labreport in labreports:
                    data = {}
                    data["id"] = labreport.id
                    data["name"] = labreport.name
                    data["description"] = labreport.description
                    data["source_entry"] = labreport.source_entry
                    data["file_field"] = None
                    data["date"] = labreport.created_at.date()
                    labreport_list.append(data)
                return labreport_list
            else:
                return [
                    {
                        "id": None,
                        "name": None,
                        "description": None,
                        "source_entry": None,
                        "file_field": None,
                        "date": None,
                    }
                ]
        else:
            return None
        
    def get_patientdocs(self, obj):
        request = self.context.get("request")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        if from_date and to_date:
            patientdocs_list = []
            patientdocs = obj.patient_docs.filter(
                created_at__date__range=[from_date, to_date]
            )
            if patientdocs:
                for patientdoc in patientdocs:
                    data = {}
                    data["id"] = patientdoc.id
                    data["name"] = patientdoc.name
                    data["description"] = patientdoc.description
                    data["source_entry"] = patientdoc.source_entry
                    data["file_field"] = None
                    data["date"] = patientdoc.created_at.date()
                    patientdocs_list.append(data)
                return patientdocs_list
            else:
                return [
                    {
                        "id": None,
                        "name": None,
                        "description": None,
                        "source_entry": None,
                        "file_field": None,
                        "date": None,
                    }
                ]
        else:
            return None
        
    def get_problems(self, obj):
        request = self.context.get("request")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        if from_date and to_date:
            problems_list = []
            problems = obj.patient_problems.filter(
                created_at__date__range=[from_date, to_date]
            )
            if problems:
                for problem in problems:
                    data = {}
                    data["id"] = problem.id
                    data["name"] = problem.name
                    data["description"] = problem.description
                    data["source_entry"] = problem.source_entry
                    data["file_field"] = None
                    data["date"] = problem.created_at.date()
                    problems_list.append(data)
                return problems_list
            else:
                return [
                    {
                        "id": None,
                        "name": None,
                        "description": None,
                        "source_entry": None,
                        "file_field": None,
                        "date": None,
                    }
                ]
        else:
            return None
        
    def get_procedures(self, obj):
        request = self.context.get("request")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        if from_date and to_date:
            procedures_list = []
            procedures = obj.patient_procedures.filter(
                created_at__date__range=[from_date, to_date]
            )
            if procedures:
                for procedure in procedures:
                    data = {}
                    data["id"] = procedure.id
                    data["name"] = procedure.name
                    data["description"] = procedure.description
                    data["source_entry"] = procedure.source_entry
                    data["file_field"] = None
                    data["date"] = procedure.created_at.date()
                    procedures_list.append(data)
                return procedures_list
            else:
                return [
                    {
                        "id": None,
                        "name": None,
                        "description": None,
                        "source_entry": None,
                        "file_field": None,
                        "date": None,
                    }
                ]
        else:
            return None

    def get_vitals(self, obj):
        request = self.context.get("request")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        result = {}
        bmi_data = []
        patient_bmi = obj.patient_bmi.filter(
            created_at__date__range=[from_date, to_date]
        )
        if patient_bmi:
            for bmi in patient_bmi:
                data = {}
                data["weight"] = bmi.weight
                data["height"] = bmi.height
                data["bmi_score"] = bmi.bmi_score
                data["height_ft"] = bmi.height_ft
                data["height_inch"] = bmi.height_inch
                data["date"] = bmi.date
                bmi_data.append(data)
            result["bmi"] = bmi_data
        else:
            bmi_data.append(
                {
                    "weight": None,
                    "height": None,
                    "height_inch": None,
                    "bmi_score": None,
                    "height_ft" : None,
                    "height_inch" : None,
                    "date" :None,
                }
            )
            result["bmi"] = bmi_data

        bloodpressure_data = []
        patient_bloodpressure = obj.patient_blood_pressure.filter(
            created_at__date__range=[from_date, to_date]
        )
        if patient_bloodpressure:
            for bloodpressure in patient_bloodpressure:
                data = {}
                data["pulse"] = bloodpressure.pulse
                data["systolic"] = bloodpressure.systolic
                data["diastolic"] = bloodpressure.diastolic
                data["date"] = bloodpressure.date
                bloodpressure_data.append(data)
            result["bloodpressure"] = bloodpressure_data
        else:
            bloodpressure_data.append(
                {"pulse": None, "systolic": None, "diastolic": None, "date":None}
            )
            result["bloodpressure"] = bloodpressure_data

        cholesterol_data = []
        patient_cholesterol = obj.patient_cholesterol.filter(
            created_at__date__range=[from_date, to_date]
        )
        if patient_cholesterol:
            for cholesterol in patient_cholesterol:
                data = {}
                data["total_cholesterol"] = cholesterol.total_cholesterol
                data["triglycerides"] = cholesterol.triglycerides
                data["hdl"] = cholesterol.hdl
                data["ldl"] = cholesterol.ldl
                data["date"] = cholesterol.date
                cholesterol_data.append(data)
            result["cholesterol"] = cholesterol_data
        else:
            cholesterol_data.append(
                {
                    "total_cholesterol": None,
                    "triglycerides": None,
                    "hdl": None,
                    "ldl": None,
                    "date": None,
                }
            )
            result["cholesterol"] = cholesterol_data

        bloodglucose_data = []
        patient_glucose = obj.patient_blood_glucose.filter(
            created_at__date__range=[from_date, to_date]
        )
        if patient_glucose:
            for glucose in patient_glucose:
                data = {}
                data["blood_sugar"] = glucose.blood_sugar
                data["test_type"] = glucose.test_type
                data["date"] = glucose.date
                bloodglucose_data.append(data)
            result["bloodglucose"] = bloodglucose_data
        else:
            bloodglucose_data.append({"blood_sugar": None, "test_type": None, "date":None})
            result["bloodglucose"] = bloodglucose_data
            
        pulse_ox_data = []
        patient_pulse_ox = obj.patient_pulseOx.filter(
            created_at__date__range=[from_date, to_date]
        )
        if patient_pulse_ox:
            for pulseox in patient_pulse_ox:
                data = {}
                data["spo2"] = pulseox.spo2
                data["pulse_rate"] = pulseox.pulse_rate
                data["spo2_value"] = pulseox.spo2_value
                data["source_entry"] = pulseox.source_entry
                data["date"] = pulseox.date
                pulse_ox_data.append(data)
            result["pulseOx"] = pulse_ox_data
        else:
            pulse_ox_data.append({"spo2": None, "pulse_rate": None,"spo2_value":None,"source_entry":None,"date":None})
            result["pulseOx"] = pulse_ox_data
            
        hba1c_data = []
        patient_hba1c = obj.patient_hba1c.filter(
            created_at__date__range=[from_date, to_date]
        )
        if patient_hba1c:
            for hba1c in patient_hba1c:
                data = {}
                data["hbaic"] = hba1c.hbaic
                data["source_entry"] = hba1c.source_entry
                data["date"] = hba1c.date
                hba1c_data.append(data)
            result["hba1c"] = hba1c_data
        else:
            hba1c_data.append({"hbaic": None, "source_entry": None, "date":None})
            result["hba1c"] = hba1c_data

        return result
    
    def get_self_management_goals(self, obj):
        request = self.context.get("request")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        goal_list = []
        obj = obj.patient_goal.filter(
            created_at__date__range=[from_date, to_date]
        )
        if obj:
            for goal in obj:
                dict = {}
                dict["goal_name"] = goal.name
                dict["goal_date"] = goal.goal_date.date()
                dict["goal_status"] = goal.get_goal_status_display()
                goal_list.append(dict)
            return goal_list
        else:
            return [{"goal_name": None, "goal_date": None, "goal_status": None}]

    def get_details(self, obj):
        if obj.patient_patientprovidermapping.first():
            provider_name = (
                obj.patient_patientprovidermapping.first().primary_provider.user.first_name
            )
            return provider_name
        else:
            return [{"detail_list": None}]
        
    def get_assessment(self, obj):
        request = self.context.get("request")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        assessment = Assessment.objects.filter(patient=obj, is_active = True, created_at__date__range=[from_date, to_date])
        # assessment = obj.patient_assessment.filter(
        #     created_at__date__range = [from_date, to_date]
        #     )
        if assessment:
            serializer = ListPatientAssessmentSerializer(assessment, many=True)
            assessment_data = serializer.data
        else:
            assessment_data = {
                "assessment_name":None, 
                "date":None, 
                "score":None, 
                "assessment_status":None, 
                "time_spent":None, 
                "severity":None 
            }
        return assessment_data
        
    def get_caregap(self, obj):
        request = self.context.get("request")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        caregap_list = []
        patient_caregap = AnnualWellnessVist.objects.filter(
            patient=obj, created_at__date__range=[from_date, to_date], 
        )
        if patient_caregap:
            for caregap in patient_caregap:
                if caregap.date_of_last_services or caregap.need or caregap.completed_by_date:
                    dict = {}
                    dict["services_and_Screening_name"] = caregap.services_and_Screening_name.name
                    dict["date_of_last_services"] = caregap.date_of_last_services
                    dict["who"] = caregap.who
                    dict["often"] = caregap.often
                    dict["next_schedule_date"] = caregap.next_schedule_date
                    dict["need"] = caregap.need
                    dict["completed_by_date"] = caregap.completed_by_date
                    dict["annual_wellness_status"] = caregap.annual_wellness_status
                    caregap_list.append(dict)
            if len(caregap_list) > 0:
                return caregap_list
            else:
                return [{"services_and_Screening_name": None, "date_of_last_services": None, "who": None,"often":None,"next_schedule_date":None,"need":None,"completed_by_date":None,"annual_wellness_status":None}]    
        else:
            return [{"services_and_Screening_name": None, "date_of_last_services": None, "who": None,"often":None,"next_schedule_date":None,"need":None,"completed_by_date":None,"annual_wellness_status":None}]

    def get_manual_log(self, obj, format=None):
        request = self.context.get("request")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        try:
            if from_date and to_date:
                vcall = VitalCallLog.objects.filter(patient=obj, created_at__date__range=[from_date, to_date])
                mcall = MedicalConditionCallLog.objects.filter(patient=obj, created_at__date__range=[from_date, to_date])
                acall = Assessment.objects.filter(patient=obj, created_at__date__range=[from_date, to_date])
                awvcall = AnnualWellnessVisitCallLog.objects.filter(patient=obj, created_at__date__range=[from_date, to_date])
                smpcall = SelfManagementPlanCallLog.objects.filter(patient=obj, created_at__date__range=[from_date, to_date])
                taskcall = Task.objects.filter(patient=obj, created_at__date__range=[from_date, to_date])
                outreachcall = PatientOutreach.objects.filter(patient=obj, created_at__date__range=[from_date, to_date])
                result = get_call_types(obj, vcall, mcall, acall, awvcall, smpcall, taskcall, outreachcall)
            return result
        except Exception as e:
            return []
    
    def get_session_log(self, obj):
        request = self.context.get("request")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        data = []
        patient_sessions = PatientSession.objects.filter(
            patient=obj, created_at__date__range=[from_date, to_date]
        )

        if patient_sessions:
            for ps in patient_sessions:
                session_data = {}
                session_data["id"] = ps.id
                session_data["session_id"] = ps.session_id
                # session_data["duration"] = ps.duration.seconds // 60
                session_data["duration"] = str(ps.duration) 
                session_data["date_and_time"] = ps.created_at
                data.append(session_data)
            return data
        else:
            return [{"id":None,"session_id":None,"duration":None,"date_and_time":None}]


class StepsToAchieveGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = StepsToAchieveGoal
        fields = "__all__"


class GoalChallengesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalChallenges
        fields = "__all__"


class AssistanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assistance
        fields = "__all__"

    # class PatientMonthlyReportSerializer(serializers.ModelSerializer):


#     medication_s_no = serializers.SerializerMethodField()
#     medication_name = serializers.SerializerMethodField()
#     medication_dose = serializers.SerializerMethodField()
#     medication_type = serializers.SerializerMethodField()
#     medication_frequency = serializers.SerializerMethodField()
#     medication_prescriber = serializers.SerializerMethodField()
#     medication_status = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Patient
#         fields = ['medication_name', 'medication_s_no', 'medication_dose', 'medication_type',
#                   'medication_frequency', 'medication_prescriber', 'medication_status']
#
#     def get_medication_s_no(self, obj):
#         data_li = []
#         medication_id = obj.patient_medication.all()
#         for name in medication_id:
#             data = {}
#             data['id'] = name.id
#             data_li.append(data)
#         return data_li
#
#     def get_medication_name(self, obj):
#         data_li = []
#         medication_name = obj.patient_medication.all()
#         for name in medication_name:
#             data = {}
#             data['name'] = name.medication_name
#             data_li.append(data)
#         return data_li
#
#     def get_medication_dose(self, obj):
#         l1 = []
#
#         medication_dose = obj.patient_medication.all()
#         for name in medication_dose:
#             l1.append(name.dose)
#         return (l1)
#
#     def get_medication_type(self, obj):
#         l1 = []
#         medication_type = obj.patient_medication.all()
#         for name in medication_type:
#             l1.append(name.type)
#         return (l1)
#
#     def get_medication_frequency(self, obj):
#         l1 = []
#         medication_frequency = obj.patient_medication.all()
#         for name in medication_frequency:
#             l1.append(name.frequency)
#         return (l1)
#
#     def get_medication_prescriber(self, obj):
#         l1 = []
#         medication_prescriber = obj.patient_medication.all()
#         for name in medication_prescriber:
#             l1.append(name.prescriber.user.first_name)
#         return (l1)
#
#     def get_medication_status(self, obj):
#         l1 = []
#         medication_status = obj.patient_medication.all()
#         for name in medication_status:
#             l1.append(name.is_active)
#         return (l1)


class VitalCallLogSerializer(serializers.ModelSerializer):
    call_duration = serializers.SerializerMethodField()
    class Meta:
        model = VitalCallLog
        fields = "__all__"        
    
    def get_call_duration(self, obj):
        return obj.call_duration.seconds // 60     


class MedicationCallLogSerializer(serializers.ModelSerializer):
    call_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicalConditionCallLog
        fields = "__all__"
        
    def get_call_duration(self, obj):
        return obj.call_duration.seconds // 60       


class GetPatientCallLogsListSerializer(serializers.Serializer):
    patient_call_log = serializers.SerializerMethodField()
    vital_call_log = serializers.SerializerMethodField()
    medicalcondition_call_log = serializers.SerializerMethodField()
    assessment_call_log = serializers.SerializerMethodField()
    selfmanagementplan_call_log = serializers.SerializerMethodField()
    annualwellnessvisit_call_log = serializers.SerializerMethodField()

    class Meta:
        # model = PatientCallLog
        field = (
            "patient_call_log",
            "vital_call_log",
            "medicalcondition_call_log",
            "assessment_call_log",
            "selfmanagementplan_call_log",
            "annualwellnessvisit_call_log",
        )

    def get_patient_call_log(self, obj):
        list = []
        for patientcall_log in obj.patient_patientcall_log.all():
            dict = {}
            dict["name"] = patientcall_log.agenda
            dict["call_duration"] = patientcall_log.call_duration
            dict["created_at"] = patientcall_log.created_at
            list.append(dict)
        return list

    def get_vital_call_log(self, obj):
        list = []
        for patient_vitalcall_log in obj.patient_vitalcall_log.all():
            dict = {}
            dict["name"] = "vital"
            dict["call_duration"] = patient_vitalcall_log.call_duration
            dict["created_at"] = patient_vitalcall_log.created_at
            list.append(dict)
        return list

    def get_medicalcondition_call_log(self, obj):
        list = []
        for (
            patient_medicalconditioncalllog
        ) in obj.patient_medicalconditioncalllog.all():
            dict = {}
            dict["name"] = "xyz"
            dict["call_duration"] = patient_medicalconditioncalllog.call_duration
            dict["created_at"] = patient_medicalconditioncalllog.created_at
            list.append(dict)
        return list

    def get_assessment_call_log(self, obj):
        list = []
        for patient_assessmentcalllog in obj.patient_assessmentcalllog.all():
            dict = {}
            dict["name"] = "xyz"
            dict["call_duration"] = patient_assessmentcalllog.call_duration
            dict["created_at"] = patient_assessmentcalllog.created_at
            list.append(dict)
        return list

    def get_selfmanagementplan_call_log(self, obj):
        list = []
        for (
            patient_selfmanagementplancalllog
        ) in obj.patient_selfmanagementplancalllog.all():
            dict = {}
            dict["name"] = "xyz"
            dict["call_duration"] = patient_selfmanagementplancalllog.call_duration
            dict["created_at"] = patient_selfmanagementplancalllog.created_at
            list.append(dict)
        return list

    def get_annualwellnessvisit_call_log(self, obj):
        list = []
        for (
            patient_annualwellnessvisit_calllog
        ) in obj.patient_annualwellnessvisit_calllog.all():
            dict = {}
            dict["name"] = "xyz"
            dict["call_duration"] = patient_annualwellnessvisit_calllog.call_duration
            dict["created_at"] = patient_annualwellnessvisit_calllog.created_at
            list.append(dict)
        return list


class ScreeningNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreeningName
        fields = ["id", "name"]


class AssessmentCallLogSerializer(serializers.ModelSerializer):
    call_duration = serializers.SerializerMethodField()
    class Meta:
        model = AssessmentCallLog
        fields = "__all__"
        
    def get_call_duration(self, obj):
        return obj.call_duration.seconds // 60    


class AnnualWellnessVisitCallLogSerializer(serializers.ModelSerializer):
    call_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = AnnualWellnessVisitCallLog
        fields = "__all__"
        
    def get_call_duration(self, obj):
        return obj.call_duration.seconds // 60       


class SelfManagementPlanCallLogSerializer(serializers.ModelSerializer):
    call_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = SelfManagementPlanCallLog
        fields = ['id', 'patient', 'care_manager', 'call_duration', 'notes', 'date']

    def get_call_duration(self, obj):
        return obj.call_duration.seconds // 60


class DailyOutreachSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyOutreach
        fields = '__all__'


class RecurrenceDailyOutreachSerializer(serializers.ModelSerializer):
    patient = serializers.CharField()
    contact_date = serializers.DateField()
    schedule_follow_up_date = serializers.DateField(required=False)
    contact_type = serializers.CharField(max_length=80)
    time_spent = serializers.CharField(max_length=50)
    notes = serializers.CharField(max_length=1225)
    outreach_status = serializers.CharField(max_length=50)
    recurrence_pattern = serializers.BooleanField()
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    daily = DailyOutreachSerializer()
    care_manager = serializers.CharField(required=False)

    class Meta:
        model = DailyOutreach
        fields = ['weekday', 'weekend',
        'patient', 'contact_date', 'schedule_follow_up_date', 'contact_type',
                'time_spent', 'notes', 'outreach_status', 'recurrence_pattern',
                'from_date', 'to_date', 'care_manager',
                'daily'
        ]

    def validate_patient(self, patient):
        patient_obj = None
        if patient:
            patient_obj = Patient.objects.filter(id=patient).last()
        return patient_obj

    def create(self, validated_data, *args, **kwargs):
        patient = self.validated_data.get('patient', None)
        name = self.validated_data.get('contact_type', None)
        notes = self.validated_data.get('notes', None)
        contact_date = self.validated_data.get('date', None)
        time_spent = self.validated_data.get('time_spent', None)
        care_manager = validated_data.get('care_manager')
        from_date = self.validated_data.get('from_date', None)
        to_date = self.validated_data.get('to_date', None)
        daily = self.validated_data.pop('daily', None)
        weekends_weekdays = [key for key, val in daily.items()]
        daily_obj = DailyOutreach.objects.create(**daily)
        outreach_obj = PatientOutreach.objects.create(**self.validated_data)
        outreach_obj.daily = daily_obj
        outreach_obj.care_manager = care_manager
        outreach_obj.save()
        result_key, results = get_weekends_weedays(weekends_weekdays, from_date, to_date)
        for result in results:
            task = Task.objects.create(
                patient = patient,
                name = name,
                notes = notes,
                date = contact_date,
                follow_up_date = result.date(),
                time_spent = '0',
                task_date = result.date(),
                care_manager = care_manager,
            )
            task.time_spent = datetime.timedelta(minutes=int(task.time_spent))
            task.save()
        return outreach_obj


class WeeklyOutreachSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyOutreach
        fields = '__all__'


class RecurrencWeeklyOutreachSerializer(serializers.ModelSerializer):
    patient = serializers.CharField()
    contact_date = serializers.DateField()
    schedule_follow_up_date = serializers.DateField(required=False)
    contact_type = serializers.CharField(max_length=80)
    time_spent = serializers.CharField(max_length=50)
    notes = serializers.CharField(max_length=1225)
    outreach_status = serializers.CharField(max_length=50)
    recurrence_pattern = serializers.BooleanField()
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    weekly = WeeklyOutreachSerializer()
    care_manager = serializers.CharField(required=False)
    
    class Meta:
        model = WeeklyOutreach
        fields = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday',
        'friday', 'saturday',
        'patient', 'contact_date', 'schedule_follow_up_date', 'contact_type',
                'time_spent', 'notes', 'outreach_status', 'recurrence_pattern',
                'from_date', 'to_date', 'care_manager',
                'weekly'
        ]

    def validate_patient(self, patient):
        patient_obj = None
        if patient:
            patient_obj = Patient.objects.filter(id=patient).last()
        return patient_obj


    def create(self, validated_data, *args, **kwargs):
        patient = self.validated_data.get('patient', None)
        name = self.validated_data.get('contact_type', None)
        notes = self.validated_data.get('notes', None)
        contact_date = self.validated_data.get('date', None)
        time_spent = self.validated_data.get('time_spent', None)
        care_manager = validated_data.get('care_manager')
        from_date = self.validated_data.get('from_date', None)
        to_date = self.validated_data.get('to_date', None)
        weekly = self.validated_data.pop('weekly', None)
        days = [key for key, val in weekly.items()]
        weekly_obj = WeeklyOutreach.objects.create(**weekly)
        outreach_obj = PatientOutreach.objects.create(**self.validated_data)
        outreach_obj.weekly = weekly_obj
        outreach_obj.care_manager = care_manager
        outreach_obj.save()
        result_key, results = get_days(days, from_date, to_date)
        for result in results:
            task = Task.objects.create(
                patient = patient,
                name = name,
                notes = notes,
                date = contact_date,
                follow_up_date = result.date(),
                time_spent = '0',
                task_date = result.date(),
                care_manager = care_manager,
            )
            task.time_spent = datetime.timedelta(minutes=int(task.time_spent))
            task.save()
        return outreach_obj


class RecurrencMonthlyOutreachSerializer(serializers.ModelSerializer):

    class Meta:
        model = PatientOutreach
        fields = [
            "id",
            "patient",
            "contact_date",
            "schedule_follow_up_date",
            "contact_type",
            "time_spent",
            "notes",
            "outreach_status",
            "recurrence_pattern",
            "from_date",
            "to_date",
            "care_manager",
            "monthly",
        ]

    def create(self, validated_data):
        patient = validated_data.get('patient', None)
        name = validated_data.get('contact_type', None)
        notes = validated_data.get('notes', None)
        contact_date = validated_data.get('date', None)
        time_spent = validated_data.get('time_spent', None)
        care_manager = validated_data.get('care_manager', None)
        from_date = self.validated_data.get('from_date', None)
        to_date = self.validated_data.get('to_date', None)
        monthly = self.validated_data.get('monthly', None)
        if monthly:
            outreach_obj = PatientOutreach.objects.create(**self.validated_data)
            outreach_obj.care_manager = care_manager
            outreach_obj.save()
            results = get_next_months_date(from_date, to_date)
            for result in results:
                Task.objects.create(
                    patient = patient,
                    name = name,
                    notes = notes,
                    date = contact_date,
                    follow_up_date = result,
                    time_spent = '0',
                    task_date = result,
                    care_manager = care_manager,
                )
            return outreach_obj
        else:
            return 0


class RecurrencBiWeeklyOutreachSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientOutreach
        fields = [
            "id",
            "patient",
            "contact_date",
            "schedule_follow_up_date",
            "contact_type",
            "time_spent",
            "notes",
            "outreach_status",
            "recurrence_pattern",
            "from_date",
            "to_date",
            "care_manager",
            "bi_weekly",
        ]

    def create(self, validated_data):
        patient = validated_data.get('patient', None)
        name = validated_data.get('contact_type', None)
        notes = validated_data.get('notes', None)
        contact_date = validated_data.get('date', None)
        care_manager = validated_data.get('care_manager', None)
        from_date = self.validated_data.get('from_date', None)
        to_date = self.validated_data.get('to_date', None)
        bi_weekly = self.validated_data.get('bi_weekly', None)
        days = self.context.get('data')
        days = [key for key, val in days.items()]
        results = get_bi_weekly_days(days, from_date, to_date)
        if bi_weekly:
            outreach_obj = PatientOutreach.objects.create(**self.validated_data)
            outreach_obj.care_manager = care_manager
            outreach_obj.save()
            for result in results:
                Task.objects.create(
                    patient = patient,
                    name = name,
                    notes = notes,
                    date = contact_date,
                    follow_up_date = result,
                    time_spent = '0',
                    task_date = result,
                    care_manager = care_manager,
                )
            return outreach_obj
        else:
            return 0


class PatientOutreachSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    time_spents = serializers.SerializerMethodField()

    class Meta:
        model = PatientOutreach
        fields = [
            "id",
            "patient_name",
            "patient",
            "contact_date",
            "schedule_follow_up_date",
            "contact_type",
            "outcome",
            "provider",
            "time_spent",
            "notes",
            "patientoutreach_status",
            "outreach_status",
            "time_spents",
            "resolution_action",
            "outreach_name",
            "care_program",
            "care_program_from_date",
            "care_program_to_date",
            "care_member",
            "care_manager",
            "recurrence_pattern",
            "daily",
            "from_date",
            "to_date",
        ]

    def create(self, validated_data):
        today = datetime.date.today()
        schedule_follow_up_date = validated_data.get('schedule_follow_up_date', None)
        patient = validated_data.get('patient', None)
        name = validated_data.get('contact_type', None)
        notes = validated_data.get('notes', None)
        care_manager = validated_data.get('care_manager', None)
        time_spent = validated_data.get('time_spent', None)
        contact_date = validated_data.get('date', None)
        if schedule_follow_up_date:
            if schedule_follow_up_date > today:
                task = Task.objects.create(
                    patient = patient,
                    name = name,
                    notes = notes,
                    date = contact_date,
                    follow_up_date = schedule_follow_up_date,
                    time_spent = '0',
                    care_manager = care_manager,
                )
                task.time_spent = datetime.timedelta(minutes=int(task.time_spent))
                task.save()
                outreach = PatientOutreach.objects.create(**validated_data)
                return outreach
            else:
                outreach = PatientOutreach.objects.create(**validated_data)
                return outreach
        else:
            outreach = PatientOutreach.objects.create(**validated_data)
            return outreach


    def get_patient_name(self, obj):
        patient_fullname = None
        patient = Patient.objects.filter(id=obj.patient_id).last()
        if patient is not None:
            patient_fullname = (
                str(patient.user.first_name) + " " + str(patient.user.last_name)
            )
        return patient_fullname
    
    def get_time_spents(self, obj):
        return obj.time_spent.seconds // 60


class PatientOutreachUpdateSerializer(serializers.ModelSerializer):
    # time_spents = serializers.SerializerMethodField()

    class Meta:
        model = PatientOutreach
        fields = [
            "time_spent",
            "notes",
        ]



class OutreachSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = PatientOutreach
        fields = [
            "patient_name",
            "patient",
            "contact_date",
            "schedule_follow_up_date",
            "contact_type",
            "resolution_action",
            "outcome",
            "provider",
            "time_spent",
            "notes",
            "care_program",
            "care_program_from_date",
            "care_program_to_date",
            "care_member",
            "patientoutreach_status",
            "outreach_status",
        ]

    def get_patient_name(self, patient):
        patient_fullname = None
        if patient is not None:
            patient_fullname = (
                str(patient.patient.user.first_name)
                + " "
                + str(patient.patient.user.last_name)
            )
        return patient_fullname


class PatientOutreachListSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()
    time_spent = serializers.SerializerMethodField()
    daily = serializers.SerializerMethodField()

    class Meta:
        model = PatientOutreach
        fields = [
            "id",
            "patient_name",
            "patient",
            "profile_pic",
            "contact_date",
            "schedule_follow_up_date",
            "contact_type",
            "resolution_action",
            "outcome",
            "provider",
            "time_spent",
            "notes",
            "patientoutreach_status",
            "outreach_status",
            "recurrence_pattern",
            "daily",
            "care_manager",
            "from_date",
            "to_date"
        ]

    def get_profile_pic(self, obj):
        patient = Patient.objects.filter(id=obj.patient.id).last()
        if patient.user.profile_pic:
            return settings.BACKEND_URL + obj.patient.user.profile_pic.url
        else:
            return None

    def get_patient_name(self, obj):
        patient_fullname = None
        patient = Patient.objects.filter(id=obj.patient_id).last()
        if patient is not None:
            patient_fullname = (
                str(patient.user.first_name) + " " + str(patient.user.last_name)
            )
        return patient_fullname
    
    def get_time_spent(self, obj):
        return obj.time_spent.seconds // 60

    def get_daily(self, obj):

        if obj.daily:
            daily = {
                "id": obj.daily.id if obj.daily else None,
                "weekday": obj.daily.weekday if obj.daily else None,
                "weekend": obj.daily.weekend if obj.daily else None,
                "from_date": obj.daily.from_date if obj.daily else None,
                "to_date": obj.daily.to_date if obj.daily else None,
            }
            return daily
        else:
            return None

# inprogress
class UpdatePatientOutreachStatusSerializer(serializers.ModelSerializer):
    patientoutreach_status = serializers.SerializerMethodField()

    class Meta:
        model = PatientOutreach
        fields = ["patientoutreach_status"]

    def get_patientoutreach_status(self, obj):
        pass


class PatientDetailSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    home_phone = serializers.SerializerMethodField()
    medicaid_id = serializers.SerializerMethodField()
    medicare_id = serializers.SerializerMethodField()
    primary_insurance = serializers.SerializerMethodField()
    secondary_email = serializers.SerializerMethodField()
    cell_phone = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    zip_code = serializers.SerializerMethodField()
    address_1 = serializers.SerializerMethodField()
    address_2 = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()

    primary_provider = serializers.SerializerMethodField()
    secondary_provider = serializers.SerializerMethodField()

    communication = serializers.SerializerMethodField()
    caremanager = serializers.SerializerMethodField()
    primary_insurance_id =  serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = (
            "id",
            "title",
            "first_name",
            "middle_name",
            "last_name",
            "dob",
            "gender",
            "profile_pic",
            "email",
            "home_phone",
            "medicaid_id",
            "medicare_id",
            "primary_insurance",
            "secondary_email",
            "cell_phone",
            "state",
            "zip_code",
            "address_1",
            "address_2",
            "city",
            "primary_provider",
            "secondary_provider",
            "communication",
            "caremanager",
            "primary_insurance_id",
            "caremanager_obj"
        )

    def get_home_phone(self, obj):

        for patient_detail in obj.patient_contact_detail.all():
            home_phone = patient_detail.home_phone
            return home_phone

    def get_medicaid_id(self, obj):
        for patient_detail in obj.patient_contact_detail.all():
            medicaid_id = patient_detail.medicaid_id
            return medicaid_id

    def get_medicare_id(self, obj):
        for patient_detail in obj.patient_contact_detail.all():
            medicare_id = patient_detail.medicare_id
            return medicare_id

    def get_primary_insurance(self, obj):
        for patient_detail in obj.patient_contact_detail.all():
            primary_insurance = patient_detail.primary_insurance
            return primary_insurance

    def get_secondary_email(self, obj):
        for patient_detail in obj.patient_contact_detail.all():
            secondary_email = patient_detail.secondary_email
            return secondary_email

    def get_cell_phone(self, obj):
        for patient_detail in obj.patient_contact_detail.all():
            cell_phone = patient_detail.cell_phone
            return cell_phone

    def get_state(self, obj):
        for patient_detail in obj.patient_contact_detail.all():
            state = patient_detail.state
            return state

    def get_zip_code(self, obj):
        for patient_detail in obj.patient_contact_detail.all():
            zip_code = patient_detail.zip_code
            return zip_code

    def get_address_1(self, obj):
        for patient_detail in obj.patient_contact_detail.all():
            address_1 = patient_detail.address_1
            return address_1

    def get_address_2(self, obj):
        for patient_detail in obj.patient_contact_detail.all():
            address_2 = patient_detail.address_2
            return address_2

    def get_city(self, obj):
        for patient_detail in obj.patient_contact_detail.all():
            city = patient_detail.city
            return city

    def get_primary_provider(self, obj):
        list = []
        if obj.patient_patientprovidermapping.all():
            for patient_mapping in obj.patient_patientprovidermapping.all():
                dict = {}
                if patient_mapping.primary_provider:
                    dict["name"] = patient_mapping.primary_provider.user.first_name
                    dict["id"] = patient_mapping.primary_provider.id
                    list.append(dict)
                else:
                    return list
            return list
        else:
            return list

    def get_secondary_provider(self, obj):
        list = []
        if PatientProviderMapping.objects.filter(patient=obj).last():
            ppm_sec = (
                PatientProviderMapping.objects.filter(patient=obj)
                .last()
                .secondary_provider
            )
            if ppm_sec:
                for patient_mapping in obj.patient_patientprovidermapping.all():
                    dict = {}
                    dict["name"] = patient_mapping.secondary_provider.user.first_name
                    dict["id"] = patient_mapping.secondary_provider.id
                    list.append(dict)
            return list
        else:
            return list

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_profile_pic(self, obj):
        if obj.user.profile_pic:
            return settings.BACKEND_URL + obj.user.profile_pic.url
        else:
            return None

    def get_email(self, obj):
        return obj.user.email

    def get_communication(self, obj):
        for patient_detail in obj.patient_contact_detail.all():
            communication = [
                {
                    "id": communication.id,
                    "communication_type": communication.communication_type,
                }
                for communication in patient_detail.communication.all()
            ]
            return communication

    # Get logged in caremanger
    def get_caremanager(self, obj):

        
        # request = self.context.get("request")

        # cm = CareManager.objects.filter(user=request.user).last()
        # assign_hospital_to_cm = cm.hospital
        # hospitals = HospitalBranch.objects.filter(hospital=assign_hospital_to_cm,care_manager=cm)
        # care_managers_of_login_user_hospital = [
        #     {
        #         "id": hospital.care_manager.id,
        #         "care_manager_name": str(hospital.care_manager.user.first_name)
        #         + " "
        #         + str(hospital.care_manager.user.last_name),
        #     }
        #     for hospital in hospitals
        # ]
        # return care_managers_of_login_user_hospital

        care_managers_of_login_user_hospital ={
                "id": obj.caremanager_obj.id,
                "care_manager_name": obj.caremanager_obj.user.first_name
                + " "
                + obj.caremanager_obj.user.last_name,
            }
        
        return care_managers_of_login_user_hospital



    def get_primary_insurance_id(self, obj):
        for patient_detail in obj.patient_contact_detail.all():
            primary_insurance_id = patient_detail.primary_insurance_id
            return primary_insurance_id

  
class PatientCallLogWithTypeSerializer(serializers.ModelSerializer):
    all_logs = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ["all_logs"]

    def get_all_logs(self, obj, format=None):
        request = self.context.get("request")
        month = request.query_params.get("month")
        call_type = request.query_params.get("type")
        today = datetime.date.today()
        try:
            if month and call_type:
                vcall = VitalCallLog.objects.filter(patient=obj, created_at__month = month)
                mcall = MedicalConditionCallLog.objects.filter(patient=obj, created_at__month = month)
                acall = Assessment.objects.filter(patient=obj, created_at__month = month)
                awvcall = AnnualWellnessVisitCallLog.objects.filter(patient=obj, created_at__month = month)
                smpcall = SelfManagementPlanCallLog.objects.filter(patient=obj, created_at__month = month)
                taskcall = Task.objects.filter(patient=obj, created_at__month = month)
                outreachcall = PatientOutreach.objects.filter(patient=obj, created_at__month = month)
                result = get_call_types(obj, vcall, mcall, acall, awvcall, smpcall, taskcall, outreachcall)
                if call_type:
                    result = list(filter(lambda x: x['type']==call_type, result))
                    return result
                return result
            
            elif call_type:
                vcall = VitalCallLog.objects.filter(patient=obj, created_at__month = today.month)
                mcall = MedicalConditionCallLog.objects.filter(patient=obj, created_at__month = today.month)
                acall = Assessment.objects.filter(patient=obj, created_at__month = today.month)
                awvcall = AnnualWellnessVisitCallLog.objects.filter(patient=obj, created_at__month = today.month)
                smpcall = SelfManagementPlanCallLog.objects.filter(patient=obj, created_at__month = today.month)
                taskcall = Task.objects.filter(patient=obj, created_at__month = today.month)
                outreachcall = PatientOutreach.objects.filter(patient=obj, created_at__month = today.month)
                result = get_call_types(obj, vcall, mcall, acall, awvcall, smpcall, taskcall, outreachcall)
                result = list(filter(lambda x: x['type']==call_type, result))
                return result
            elif month:
                vcall = VitalCallLog.objects.filter(patient=obj, created_at__month = month)
                mcall = MedicalConditionCallLog.objects.filter(patient=obj, created_at__month = month)
                acall = Assessment.objects.filter(patient=obj, created_at__month = month)
                awvcall = AnnualWellnessVisitCallLog.objects.filter(patient=obj, created_at__month = month)
                smpcall = SelfManagementPlanCallLog.objects.filter(patient=obj, created_at__month = month)
                taskcall = Task.objects.filter(patient=obj, created_at__month = month)
                outreachcall = PatientOutreach.objects.filter(patient=obj, created_at__month = month)
                result = get_call_types(obj, vcall, mcall, acall, awvcall, smpcall, taskcall, outreachcall)
                return result
            else:
                vcall = VitalCallLog.objects.filter(patient=obj, created_at__month = today.month)
                mcall = MedicalConditionCallLog.objects.filter(patient=obj, created_at__month = today.month)
                acall = Assessment.objects.filter(patient=obj, created_at__month = today.month)
                awvcall = AnnualWellnessVisitCallLog.objects.filter(patient=obj, created_at__month = today.month)
                smpcall = SelfManagementPlanCallLog.objects.filter(patient=obj, created_at__month = today.month)
                # pcall = PatientCallLog.objects.filter(patient=obj, created_at__month = today.month)
                taskcall = Task.objects.filter(patient=obj, created_at__month = today.month)
                outreachcall = PatientOutreach.objects.filter(patient=obj, created_at__month = today.month)
                result = get_call_types(obj, vcall, mcall, acall, awvcall, smpcall, taskcall, outreachcall)
                return result
                
        except Exception as e:
            return []


class CareManagerPatientCountCallLog(serializers.ModelSerializer):
    patient_count_call_log = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ["patient_count_call_log"]

    def get_patient_count_call_log(self, obj, format=None):

        patients = self.context["data"]
        zero_to_ten = self.context["zero_to_ten"]
        eleven_to_nineteen = self.context["eleven_to_nineteen"]
        above_twenty = self.context["above_twenty"]

        result_sum = [{"patient_count": 0}]

        try:
            for patient in patients:
                vcall = VitalCallLog.objects.filter(patient=patient)
                mcall = MedicalConditionCallLog.objects.filter(patient=patient)
                acall = AssessmentCallLog.objects.filter(patient=patient)
                awvcall = AnnualWellnessVisitCallLog.objects.filter(patient=patient)
                smpcall = SelfManagementPlanCallLog.objects.filter(patient=patient)
                pcall = PatientCallLog.objects.filter(patient=patient)

                total_vcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in vcall if i.call_duration]
                )
                total_mcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in mcall if i.call_duration]
                )
                total_acall_duration = sum(
                    [i.call_duration.seconds // 60 for i in acall if i.call_duration]
                )
                total_awvcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in awvcall if i.call_duration]
                )
                total_smpcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in smpcall if i.call_duration]
                )
                total_pcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in pcall if i.call_duration]
                )
                total_call_duration = (
                    total_vcall_duration
                    + total_mcall_duration
                    + total_acall_duration
                    + total_awvcall_duration
                    + total_smpcall_duration
                )
                +total_pcall_duration

                if (
                    zero_to_ten == "0-10"
                    and total_call_duration >= 0
                    and total_call_duration <= 10
                ):
                    result_sum[0]["patient_count"] += 1
                elif (
                    eleven_to_nineteen == "11-19"
                    and total_call_duration >= 11
                    and total_call_duration <= 20
                ):
                    result_sum[0]["patient_count"] += 1
                elif above_twenty == "20" and total_call_duration > 20:
                    result_sum[0]["patient_count"] += 1

            return result_sum
        except Exception as e:
            return result_sum


class CareManagerPatientDefaultCountCallLog(serializers.ModelSerializer):
    patient_count_call_log = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ["patient_count_call_log"]

    def get_patient_count_call_log(self, obj, format=None):

        patients = self.context["data"]
        result = [{"zero_to_ten": 0}, {"eleven_to_nineteen": 0}, {"twenty_to_twenty_nine": 0}, {"thirty_to_thirty_nine": 0}, {"more_than_forty": 0}]

        try:
            for patient in patients:
                vcall = VitalCallLog.objects.filter(patient=patient, care_manager=obj)
                mcall = MedicalConditionCallLog.objects.filter(patient=patient, care_manager=obj)
                acall = AssessmentCallLog.objects.filter(patient=patient, care_manager=obj)
                awvcall = AnnualWellnessVisitCallLog.objects.filter(patient=patient, care_manager=obj)
                smpcall = SelfManagementPlanCallLog.objects.filter(patient=patient, care_manager=obj)
                pcall = PatientCallLog.objects.filter(patient=patient, care_manager=obj)

                total_vcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in vcall if i.call_duration]
                )
                total_mcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in mcall if i.call_duration]
                )
                total_acall_duration = sum(
                    [i.call_duration.seconds // 60 for i in acall if i.call_duration]
                )
                total_awvcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in awvcall if i.call_duration]
                )
                total_smpcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in smpcall if i.call_duration]
                )
                total_pcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in pcall if i.call_duration]
                )
                total_call_duration = (
                    total_vcall_duration
                    + total_mcall_duration
                    + total_acall_duration
                    + total_awvcall_duration
                    + total_smpcall_duration
                )
                +total_pcall_duration

                if total_call_duration >= 0 and total_call_duration <= 10:
                    result[0]["zero_to_ten"] += 1
                elif total_call_duration > 10 and total_call_duration < 20:
                    result[1]["eleven_to_nineteen"] += 1
                elif total_call_duration > 19 and total_call_duration <= 29:
                    result[2]["twenty_to_twenty_nine"] += 1
                elif total_call_duration >= 30 and total_call_duration <= 39:
                    result[3]["thirty_to_thirty_nine"] += 1
                elif total_call_duration > 39 :
                    result[4]["more_than_forty"] += 1

            return result
        except Exception as e:
            return result


class ProblemsRetrieveSerializer(serializers.ModelSerializer):
    file_field = serializers.SerializerMethodField()

    class Meta:
        model = Problems
        fields = "__all__"

    def get_file_field(self, obj):
        if obj.file_field:
            return settings.BACKEND_URL + obj.file_field.url
        else:
            None


class ProblemsSerializer(serializers.ModelSerializer):

    file_field = serializers.SerializerMethodField()

    class Meta:
        model = Problems
        fields = "__all__"

    def get_file_field(self, obj):
        if obj.file_field:
            return settings.BACKEND_URL + obj.file_field.url


class AllergiesRetrieveSerializer(serializers.ModelSerializer):

    file_field = serializers.SerializerMethodField()

    class Meta:
        model = Allergies
        fields = "__all__"

    def get_file_field(self, obj):
        if obj.file_field:
            return settings.BACKEND_URL + obj.file_field.url


class AllergiesSerializer(serializers.ModelSerializer):

    file_field = serializers.SerializerMethodField()

    class Meta:
        model = Allergies
        fields = "__all__"

    def get_file_field(self, obj):
        if obj.file_field:
            return settings.BACKEND_URL + obj.file_field.url


class ImmunizationRetrieveSerializer(serializers.ModelSerializer):

    file_field = serializers.SerializerMethodField()

    class Meta:
        model = Immunization
        fields = "__all__"

    def get_file_field(self, obj):
        if obj.file_field:
            return settings.BACKEND_URL + obj.file_field.url


class ImmunizationSerializer(serializers.ModelSerializer):

    file_field = serializers.SerializerMethodField()

    class Meta:
        model = Immunization
        fields = "__all__"

    def get_file_field(self, obj):
        if obj.file_field:
            return settings.BACKEND_URL + obj.file_field.url


class LabReportsSerializer(serializers.ModelSerializer):

    file_field = serializers.SerializerMethodField()

    class Meta:
        model = LabReports
        fields = "__all__"

    def get_file_field(self, obj):
        if obj.file_field:
            return settings.BACKEND_URL + obj.file_field.url


class LabReportsRetrieveSerializer(serializers.ModelSerializer):
    file_field = serializers.SerializerMethodField()

    class Meta:
        model = LabReports
        fields = "__all__"

    def get_file_field(self, obj):
        if obj.file_field:
            return settings.BACKEND_URL + obj.file_field.url
        else:
            None


class ProceduresRetrieveSerializer(serializers.ModelSerializer):

    file_field = serializers.SerializerMethodField()

    class Meta:
        model = Procedures
        fields = "__all__"

    def get_file_field(self, obj):
        if obj.file_field:
            return settings.BACKEND_URL + obj.file_field.url


class ProceduresSerializer(serializers.ModelSerializer):

    file_field = serializers.SerializerMethodField()

    class Meta:
        model = Procedures
        fields = "__all__"

    def get_file_field(self, obj):
        if obj.file_field:
            return settings.BACKEND_URL + obj.file_field.url


class PatientDocssSerializer(serializers.ModelSerializer):

    file_field = serializers.SerializerMethodField()

    class Meta:
        model = PatientDocs
        fields = "__all__"

    def get_file_field(self, obj):
        if obj.file_field:
            return settings.BACKEND_URL + obj.file_field.url


class PatientDocssRetrieveSerializer(serializers.ModelSerializer):
    file_field = serializers.SerializerMethodField()

    class Meta:
        model = PatientDocs
        fields = "__all__"

    def get_file_field(self, obj):
        if obj.file_field:
            return settings.BACKEND_URL + obj.file_field.url
        else:
            None


class DefaultLoadAllIssuesSerializer(serializers.Serializer):
    allergies = serializers.SerializerMethodField()
    immunization = serializers.SerializerMethodField()
    labreports = serializers.SerializerMethodField()
    problems = serializers.SerializerMethodField()
    procedures = serializers.SerializerMethodField()
    patientdocs = serializers.SerializerMethodField()

    def get_problems(self, obj):
        patient_id = self.context.get("patient_id")
        prblms = Problems.objects.filter(patient_id=patient_id).order_by("-created_at")[
            :5
        ]
        serializer = ProblemsSerializer(prblms, many=True)
        return serializer.data

    def get_allergies(self, obj):
        patient_id = self.context.get("patient_id")
        alrgies = Allergies.objects.filter(patient_id=patient_id).order_by(
            "-created_at"
        )[:5]
        serializer = AllergiesSerializer(alrgies, many=True)
        return serializer.data

    def get_immunization(self, obj):
        patient_id = self.context.get("patient_id")
        immunizations = Immunization.objects.filter(patient_id=patient_id).order_by(
            "-created_at"
        )[:5]
        serializer = ImmunizationSerializer(immunizations, many=True)
        return serializer.data

    def get_labreports(self, obj):
        patient_id = self.context.get("patient_id")
        labrep = LabReports.objects.filter(patient_id=patient_id).order_by(
            "-created_at"
        )[:5]
        serializer = LabReportsSerializer(labrep, many=True)
        return serializer.data

    def get_procedures(self, obj):
        patient_id = self.context.get("patient_id")
        prcds = Procedures.objects.filter(patient_id=patient_id).order_by(
            "-created_at"
        )[:5]
        serializer = ProceduresSerializer(prcds, many=True)
        return serializer.data

    def get_patientdocs(self, obj):
        patient_id = self.context.get("patient_id")
        ptdcs = PatientDocs.objects.filter(patient_id=patient_id).order_by(
            "-created_at"
        )[:5]
        serializer = PatientDocssSerializer(ptdcs, many=True)
        return serializer.data


class ViewLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewLogs
        fields = "__all__"


class ViewLogsGetSerializer(serializers.Serializer):
    session_view_data = serializers.SerializerMethodField()
    view_log_data = serializers.SerializerMethodField()

    class Meta:
        fields = ["session_view_data", "view_log_data"]

    def get_view_log_data(self, obj):
        data = {}
        vlgs = ViewLogs.objects.filter(patient=obj)
        if vlgs:
            data["user_count"] = vlgs.filter(user=vlgs.last().user).count()
            data["cm_full_name"] = get_user_full_name(vlgs.last().user)
            data["user_type"] = vlgs.last().user.user_type
        else:
            data["user_count"] = None
            data["cm_full_name"] = None
            data["user_type"] = None
        return data

    def get_session_view_data(self, obj):
        data = []

        patient_sessions = PatientSession.objects.filter(patient=obj)
        if patient_sessions:
            for ps in patient_sessions:
                session_data = {}
                session_data["id"] = ps.id
                session_data["session_id"] = f"{timezone.now().strftime('%s')}_{ps.id}"
                session_data["duration"] = str(ps.duration) 
                data.append(session_data)
        return data

    # def get_last_name(self, obj):
    #     last_name = obj.user.last_name
    #     return last_name

    # def get_user_type(self, obj):
    #     user_type = obj.user.user_type
    #     return user_type

    # def get_user_count(self, obj):
    #     return user_count

    # def get_time(self, obj):
    #     date = obj.created_at
    #     return date


class UpdateGoalStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ["id", "goal_status"]


class CallLogPatientDetailSerializer(serializers.ModelSerializer):
    patient = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ["patient"]

    def get_patient(self, obj, format=None):
        result = []
        patients = self.context["data"]
        zero_to_ten = self.context["zero_to_ten"]
        eleven_to_nineteen = self.context["eleven_to_nineteen"]
        twenty_to_twenty_nine = self.context["twenty_to_twenty_nine"]
        thirty_to_thirty_nine = self.context["thirty_to_thirty_nine"]
        more_than_forty = self.context["more_than_forty"]

        try:
            for patient in patients:
                vcall = VitalCallLog.objects.filter(patient=patient, care_manager=obj)
                mcall = MedicalConditionCallLog.objects.filter(patient=patient, care_manager=obj)
                acall = AssessmentCallLog.objects.filter(patient=patient, care_manager=obj)
                awvcall = AnnualWellnessVisitCallLog.objects.filter(patient=patient, care_manager=obj)
                smpcall = SelfManagementPlanCallLog.objects.filter(patient=patient, care_manager=obj)
                pcall = PatientCallLog.objects.filter(patient=patient, care_manager=obj)

                total_vcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in vcall if i.call_duration]
                )
                total_mcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in mcall if i.call_duration]
                )
                total_acall_duration = sum(
                    [i.call_duration.seconds // 60 for i in acall if i.call_duration]
                )
                total_awvcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in awvcall if i.call_duration]
                )
                total_smpcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in smpcall if i.call_duration]
                )
                total_pcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in pcall if i.call_duration]
                )
                total_call_duration = (
                    total_vcall_duration
                    + total_mcall_duration
                    + total_acall_duration
                    + total_awvcall_duration
                    + total_smpcall_duration
                )
                +total_pcall_duration
                if (
                    zero_to_ten == "0-10"
                    and total_call_duration > 0
                    and total_call_duration <= 10
                ):
                    data = {}
                    data["id"] = patient.id
                    data["first_name"] = patient.user.first_name
                    data["last_name"] = patient.user.last_name
                    data["email"] = patient.user.email
                    result.append(data)
                elif (
                    eleven_to_nineteen == "11-19"
                    and total_call_duration > 10
                    and total_call_duration <= 19
                ):
                    data = {}
                    data["id"] = patient.id
                    data["first_name"] = patient.user.first_name
                    data["last_name"] = patient.user.last_name
                    data["email"] = patient.user.email
                    result.append(data)
                elif (
                    twenty_to_twenty_nine == "20-29"
                    and total_call_duration > 19
                    and total_call_duration <= 29
                ):
                    data = {}
                    data["id"] = patient.id
                    data["first_name"] = patient.user.first_name
                    data["last_name"] = patient.user.last_name
                    data["email"] = patient.user.email
                    result.append(data)
                elif (
                    thirty_to_thirty_nine == "30-39"
                    and total_call_duration > 29
                    and total_call_duration <= 39
                ):
                    data = {}
                    data["id"] = patient.id
                    data["first_name"] = patient.user.first_name
                    data["last_name"] = patient.user.last_name
                    data["email"] = patient.user.email
                    result.append(data)
                
                elif more_than_forty == "40" and total_call_duration >= 40:
                    data = {}
                    data["id"] = patient.id
                    data["first_name"] = patient.user.first_name
                    data["last_name"] = patient.user.last_name
                    data["email"] = patient.user.email
                    result.append(data)

            return result
        except Exception as e:
            return None


class PatientSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientSession
        fields = "__all__"


class AWVWhoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AWVWho
        fields = "__all__"


class AWVHowOftenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AWVHowOften
        fields = "__all__"


class UpdateTaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intervention
        fields = ["id", "status"]


class GetSessionWhoSerializers(serializers.ModelSerializer):
    class Meta:
        model = ScreeningWhoOften
        fields = ["screening", "who", "often"]


class CreateMannualTimeSerializer(serializers.Serializer):
    class Meta:
        fields = ["call_duration", "notes", "date"]

    def create(self, request):
        request = self.context.get("request")
        call_duration = request.data.get("call_duration")
        notes = request.data.get("notes")
        date = request.data.get("date")
        patient_id = request.data.get("patient")
        patient = Patient.objects.get(id=patient_id)

        if request.query_params.get("vitals"):
            vital = VitalCallLog.objects.create(
                call_duration=call_duration, notes=notes, date=date, patient=patient
            )
            return vital
        elif request.query_params.get("medical_condition"):
            medical_condition = MedicalConditionCallLog.objects.create(
                call_duration=call_duration, notes=notes, date=date, patient=patient
            )
            return medical_condition
        elif request.query_params.get("assessment"):
            assessment = AssessmentCallLog.objects.create(
                call_duration=call_duration, notes=notes, date=date, patient=patient
            )
            return assessment
        elif request.query_params.get("annualwellnessvisit"):
            annualwellnessvisit = AnnualWellnessVisitCallLog.objects.create(
                call_duration=call_duration, notes=notes, date=date, patient=patient
            )
            return annualwellnessvisit
        elif request.query_params.get("selfmanagementplan"):
            selfmanagementplan = SelfManagementPlanCallLog.objects.create(
                call_duration=call_duration, notes=notes, date=date, patient=patient
            )
            return selfmanagementplan
        # elif request.query_params.get('task'):
        #     task = Task.objects.create(time_spent=call_duration, notes=notes, date=date, patient=patient)
        #     return task
        # elif request.query_params.get('patientoutreach'):
        #     patientoutreach = PatientOutreach.objects.create(time_spent=call_duration, notes=notes, date=date, patient=patient)
        #     return patientoutreach
        return request.data


class CareManagerTaskSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "name",
            "date",
            "patient_name",
            "patient",
            "notes",
            "care_manager",
            "task_status",
            # "recurrence_pattern",
            "time_spent",
            "from_date",
            "to_date",
            "task_date",
            "resolution_action",
            "follow_up_date",
        ]

    def get_patient_name(self, obj):
        patient_fullname = None
        patient = Patient.objects.filter(id=obj.patient_id).last()
        if patient is not None:
            patient_fullname = (
                str(patient.user.first_name) + " " + str(patient.user.last_name)
            )
        return patient_fullname


# class PatientOutreachTaskListSerializer(serializers.Serializer):
#     tasks_outreach_data = serializers.SerializerMethodField()
#     class Meta:
#         fields = ['tasks_outreach_data']

# def get_tasks_outreach_data(self, obj):
#     result = []
#     try:
#         request = self.context["request"]
#         tasks = Task.objects.filter(care_manager=obj)
#         outreaches = PatientOutreach.objects.all()
#         task_name = request.query_params.get('task_name')
#         patient_name = request.query_params.get('patient_name')
#         task_type = request.query_params.get('task_type')

#         if patient_name:
#             tasks = Task.objects.filter(care_manager=obj, patient__user__first_name__icontains=patient_name)
#             outreaches = PatientOutreach.objects.filter(patient__user__first_name__icontains=patient_name)
#         if task_name:
#             tasks = Task.objects.filter(care_manager=obj, name__icontains=task_name)
#             outreaches = PatientOutreach.objects.filter( notes__icontains=task_name)
#         if task_type == "Task":
#             combined_queryset = list(chain(tasks))
#         elif task_type == "Outreach":
#             combined_queryset = list(chain(outreaches))
#         else:
#             combined_queryset = list(chain(tasks, outreaches))
#         print(combined_queryset)
#         result = build_task_data(combined_queryset)
#         return result
#     except Exception as e:
#         print(e)
#         return result


# def get_tasks_outreach_data(self, obj):
#     return obj


class TaskDetailUpdateSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    time_spent = serializers.SerializerMethodField()
    

    class Meta:
        model = Task
        fields = "__all__"

    def get_patient_name(self, obj):
        patient_fullname = None
        if obj is not None:
            patient_fullname = (
                str(obj.patient.user.first_name) + " " + str(obj.patient.user.last_name)
            )
        return patient_fullname
        
    def get_time_spent(self, obj):
        min = obj.time_spent.seconds // 60
        return min


class TotalMannualSerializer(serializers.ModelSerializer):
    mannual_total_time = serializers.SerializerMethodField()
    remaining_days = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    session_total_time = serializers.SerializerMethodField()
    monthly_total_time = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            "created_at",
            "name",
            "session_total_time",
            "mannual_total_time",
            "monthly_total_time",
            "remaining_days",
        ]

    def get_name(self, obj):
        return obj.user.email

    def get_session_total_time(self, obj):
        total_session_duration = get_session_total_time(obj)
        total_time = str(datetime.timedelta(seconds=total_session_duration))
        # total_time = ':'.join(str(total_time).split(':')[:2])
        return total_time

    def get_mannual_total_time(self, obj, format=None):
        total_call_duration = get_mannual_total_time(obj)
        time = str(datetime.timedelta(seconds=total_call_duration))
        # time = ':'.join(str(time).split(':')[:2])
        return time

    def get_monthly_total_time(self, obj):
        session_total_time = get_session_total_time(obj)
        total_time = get_mannual_total_time(obj)
        total_monthly_time = total_time + session_total_time
        total_monthly_time = str(datetime.timedelta(seconds=total_monthly_time))
        # total_monthly_time = ':'.join(str(total_monthly_time).split(':')[:2])
        return total_monthly_time

    def get_remaining_days(self, obj):
        today_date = datetime.datetime.now()
        current_month_days = calendar.monthrange(today_date.year, today_date.month)[1]
        remaining_days = current_month_days - today_date.day
        return remaining_days


class GeneralNotesCallLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralNotesCallLog
        fields = "__all__"


# class ProblemSerializer(serializers.Serializer):
#     problems = serializers.SerializerMethodField()

#     def get_problems(self, obj):
#         patient_id = self.context.get("patient_id")
#         prblms = Problems.objects.filter(patient_id=patient_id)
#         serializer = ProblemsSerializer(prblms, many=True)
#         return serializer.data


class AllergieSerializer(serializers.Serializer):
    allergies = serializers.SerializerMethodField()

    def get_allergies(self, obj):
        patient_id = self.context.get("patient_id")
        allergies = Allergies.objects.filter(patient_id=patient_id)
        serializer = AllergiesSerializer(allergies, many=True)
        return serializer.data


class ClinicalProfileImmunizationSerializer(serializers.Serializer):
    immunization = serializers.SerializerMethodField()

    def get_immunization(self, obj):
        patient_id = self.context.get("patient_id")
        immunizations = Immunization.objects.filter(patient_id=patient_id)
        serializer = ImmunizationSerializer(immunizations, many=True)
        return serializer.data


class SessionTimeSerializer(serializers.Serializer):
    session_view_data = serializers.SerializerMethodField()

    class Meta:
        fields = ["session_view_data"]

    def get_session_view_data(self, obj):

        data = []
        today = datetime.date.today()
        patient_sessions = PatientSession.objects.filter(
            patient=obj, created_at__year=today.year, created_at__month=today.month
        )

        if patient_sessions:
            for ps in patient_sessions:
                session_data = {}
                session_data["id"] = ps.id
                session_data["session_id"] = ps.session_id
                # session_data["duration"] = ps.duration.seconds // 60
                session_data["duration"] = str(ps.duration) 
                session_data["date_and_time"] = ps.created_at
                data.append(session_data)
            request = self.context.get("request")
            session_id = request.query_params.get("session_id")
            month = request.query_params.get("month")

            if session_id:
                session_id_data = []
                patient_search_session_id = PatientSession.objects.filter(
                    patient=obj, session_id__icontains=session_id
                )
                for ps in patient_search_session_id:
                    session_data = {}
                    session_data["id"] = ps.id
                    session_data["session_id"] = ps.session_id
                    # session_data["duration"] = ps.duration.seconds // 60
                    session_data["duration"] = str(ps.duration)
                    session_data["date and time"] = ps.created_at
                    session_id_data.append(session_data)
                return session_id_data
            elif month:
                data_by_month = []
                patient_search_session_id = PatientSession.objects.filter(
                    patient=obj, created_at__month=month
                )
                for ps in patient_search_session_id:
                    session_data = {}
                    session_data["id"] = ps.id
                    session_data["session_id"] = ps.session_id
                    # session_data["duration"] = ps.duration.seconds // 60
                    session_data["duration"] = str(ps.duration)
                    session_data["date and time"] = ps.created_at
                    data_by_month.append(session_data)
                return data_by_month
            else:
                return data


class CMTwentyMinCallLogPatientCountSerializer(serializers.ModelSerializer):
    patient_count_call_log = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ["patient_count_call_log"]

    def get_patient_count_call_log(self, obj, format=None):

        patients = self.context["data"]
        result = [{"above_twenty_min": 0}]

        try:
            for patient in patients:
                vcall = VitalCallLog.objects.filter(patient=patient)
                mcall = MedicalConditionCallLog.objects.filter(patient=patient)
                acall = AssessmentCallLog.objects.filter(patient=patient)
                awvcall = AnnualWellnessVisitCallLog.objects.filter(patient=patient)
                smpcall = SelfManagementPlanCallLog.objects.filter(patient=patient)
                pcall = PatientCallLog.objects.filter(patient=patient)

                total_vcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in vcall if i.call_duration]
                )
                total_mcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in mcall if i.call_duration]
                )
                total_acall_duration = sum(
                    [i.call_duration.seconds // 60 for i in acall if i.call_duration]
                )
                total_awvcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in awvcall if i.call_duration]
                )
                total_smpcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in smpcall if i.call_duration]
                )
                total_pcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in pcall if i.call_duration]
                )

                total_call_duration = (
                    total_vcall_duration
                    + total_mcall_duration
                    + total_acall_duration
                    + total_awvcall_duration
                    + total_smpcall_duration
                    + total_pcall_duration
                )

                if total_call_duration >= 20:
                    result[0]["above_twenty_min"] += 1

            return result
        except Exception as e:
            return result
            
            
class CareManagerNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareManagerNotes
        fields = [
            "id",
            "chronic_condition",
            "time_spent",
            "notes",
            "cm_notes_status",
            "patient",
            "care_manager",
            "caremanager_notes_date"
        ]    
        

class CareManagerDetailUpdateSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    time_spent = serializers.SerializerMethodField()


    class Meta:
        model = CareManagerNotes
        fields = "__all__"

    def get_patient_name(self, obj):
        patient_fullname = None
        if obj is not None:
            patient_fullname = (
                str(obj.patient.user.first_name) + " " + str(obj.patient.user.last_name)
            )
        return patient_fullname               

    def get_time_spent(self, obj):
        return obj.time_spent.seconds // 60


class ShowPatientDurationStatsSerializer(serializers.ModelSerializer):
    total_patients_count = serializers.SerializerMethodField()
    total_patient_over_20_minutes = serializers.SerializerMethodField()
    total_inactive_patients_count = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = (
            "total_patients_count",
            "total_patient_over_20_minutes",
            "total_inactive_patients_count",
        )

    def get_total_patients_count(self, obj):
        result = 0
        try:
            care_manager_hopital_branch = obj.hospital.hospital_branch.filter(care_manager=obj)
            patient = Patient.objects.filter(hospital=obj.hospital, caremanager__in=care_manager_hopital_branch).count()
            return patient
        except Exception as e:
            return result

    def get_total_inactive_patients_count(self, obj):
        result = 0
        try:
            care_manager_hopital_branch = obj.hospital.hospital_branch.filter(care_manager=obj)
            patients = Patient.objects.filter(hospital=obj.hospital, caremanager__in=care_manager_hopital_branch)
            ccm_declined_patient = ProgramInformation.objects.filter(program_type__program_name='CCM', program_status='DECLINED', patient__in=patients).count()
            return ccm_declined_patient
        except Exception as e:
            return result
        
    def get_total_patient_over_20_minutes(self, obj):
        result = 0
        try:
            care_manager_hopital_branch = obj.hospital.hospital_branch.filter(care_manager=obj)
            patients = Patient.objects.filter(hospital=obj.hospital, caremanager__in=care_manager_hopital_branch)
            for patient in patients:
                vcall = VitalCallLog.objects.filter(patient=patient)
                mcall = MedicalConditionCallLog.objects.filter(patient=patient)
                acall = AssessmentCallLog.objects.filter(patient=patient)
                awvcall = AnnualWellnessVisitCallLog.objects.filter(patient=patient)
                smpcall = SelfManagementPlanCallLog.objects.filter(patient=patient)
                pcall = PatientCallLog.objects.filter(patient=patient)

                total_vcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in vcall if i.call_duration]
                )
                total_mcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in mcall if i.call_duration]
                )
                total_acall_duration = sum(
                    [i.call_duration.seconds // 60 for i in acall if i.call_duration]
                )
                total_awvcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in awvcall if i.call_duration]
                )
                total_smpcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in smpcall if i.call_duration]
                )
                total_pcall_duration = sum(
                    [i.call_duration.seconds // 60 for i in pcall if i.call_duration]
                )

                total_call_duration = (
                    total_vcall_duration
                    + total_mcall_duration
                    + total_acall_duration
                    + total_awvcall_duration
                    + total_smpcall_duration
                    + total_pcall_duration
                )

                if total_call_duration >= 20:
                    result[0]["above_twenty_min"] += 1

            return result
        except Exception as e:
            return result 


class AllergiesCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergies
        fields = "__all__"


class AllergiesUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergies
        fields = "__all__"


class ImmunizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Immunization
        fields = "__all__"


class ImmunizationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Immunization
        fields = "__all__"


class LabReportsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabReports
        fields = "__all__"


class LabReportsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabReports
        fields = "__all__"


class ProceduresCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedures
        fields = "__all__"


class ProceduresUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedures
        fields = "__all__"


class PatientDocsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientDocs
        fields = "__all__"


class PatientDocsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientDocs
        fields = "__all__"


class ProblemsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problems
        fields = "__all__"


class ProblemsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problems
        fields = "__all__"


class TaskHistoryListSerializer(serializers.ModelSerializer):
    time_spent = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields  = "__all__"
    
    def get_time_spent(self, obj):
        if obj.time_spent:
            time_spent = obj.time_spent.seconds // 60
            return time_spent
        else:
            return None

        
        
class OutreachHistoryListSerializer(serializers.ModelSerializer):
    time_spent = serializers.SerializerMethodField()

    class Meta:
        model = PatientOutreach
        fields  = "__all__"
    
    def get_time_spent(self, obj):
        if obj.time_spent:
            time_spent = obj.time_spent.seconds // 60
            return time_spent
        else:
            return None
        
        
class CareManagerNotesHistoryListSerializer(serializers.ModelSerializer):
    time_spent = serializers.SerializerMethodField()
    
    class Meta:
        model = CareManagerNotes

        fields  = "__all__"                     

        fields  = "__all__"

    def get_time_spent(self, obj):
        if obj.time_spent:
            time_spent = obj.time_spent.seconds // 60
            return time_spent
        else:
            return None                   

        
        
class CareManagerCompletedMinsSerializer(serializers.ModelSerializer):
    #patient_patientcall_log=serializers.SerializerMethodField()
    class Meta:
        model=PatientCallLog
        fields = ('agenda', 'recording', 'call_start_datetime', 'call_end_datetime', 'call_duration', 'call_status', 'call_type','patient','care_manager'  )
        
        # def get_accounts_items(self, obj):
        #     customer_account_query = PatientCallLog.objects.filter(
        #        care_manager_id=obj.care_manager_id,)
        #     serializer = CareManagerCompletedMinsSerializer(customer_account_query, many=True)
    

        #     return serializer.data 

        #     return serializer.data 
        

class CoordinationPatientSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    class Meta:
        model = Patient
        fields = ["id", "first_name", "last_name"]

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name
            

class UnassignProviderPatientSerializer(serializers.ModelSerializer):
    provider = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ["id", "name", "provider"]

    def get_provider(self, obj):
        provider = obj.patient_patientprovidermapping.all()[0]
        if provider.primary_provider:
            provider_name = provider.primary_provider.user.get_full_name()
            return provider_name
        else:
            return None

    def get_name(self, obj):
        return obj.user.get_full_name()
 
 
class DailyGoalTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyGoalTask
        fields = '__all__'    


class AddDailyGoalTaskSerializer(serializers.Serializer):
    patient = serializers.CharField() #
    care_manager = serializers.CharField(required=False)
    goal = serializers.CharField(required=False)
    date = serializers.DateField()#
    schedule_follow_up_date = serializers.DateField(required=False)
    contact_type = serializers.CharField(max_length=80) #
    time_spent = serializers.CharField(max_length=50)
    notes = serializers.CharField(max_length=1225) #
    status = serializers.CharField(max_length=50) #
    recurrence_pattern = serializers.BooleanField() #
    daily = DailyGoalTaskSerializer(many=True) #
    from_date = serializers.DateField() #
    to_date = serializers.DateField() #    
    

    class Meta:
        model = DailyOutreach
        fields = ['weekday', 'weekend',
        'patient', 'contact_date', 'schedule_follow_up_date', 'contact_type',
                'time_spent', 'notes', 'status', 'recurrence_pattern',
                'from_date', 'to_date', 'care_manager',
                'daily', 'goal', 'date'
        ]

    def validate_patient(self, patient):
        patient_obj = None
        if patient:
            patient_obj = Patient.objects.filter(id=patient).last()
        return patient_obj

    def validate_goal(self, goal):
        goal_obj = None
        if goal:
            goal_obj = Goal.objects.filter(id=goal).last()
        return goal_obj
    
    def create(self, validated_data, *args, **kwargs):
        patient = self.validated_data.get('patient', None)
        name = self.validated_data.get('contact_type', None)
        notes = self.validated_data.get('notes', None)
        contact_date = self.validated_data.get('date', None)
        time_spent = self.validated_data.get('time_spent', None)
        care_manager = validated_data.get('care_manager')
        from_date = self.validated_data.get('from_date', None)
        to_date = self.validated_data.get('to_date', None)
        daily = self.validated_data.pop('daily', None)[0]
        
        goal_id = self.validated_data.get('goal', None)        
        # goal_obj = Goal.objects.filter(id=goal_id).last()
        weekends_weekdays = [key for key, val in daily.items()]
        daily_obj = DailyGoalTask.objects.create(**daily)
        goaltask_obj = GoalTask.objects.create(**self.validated_data)
        goaltask_obj.daily = daily_obj
        goaltask_obj.care_manager = care_manager
        # goaltask_obj.goal = goal_obj
        goaltask_obj.save()
        result_key, results = get_weekends_weedays(weekends_weekdays, from_date, to_date)
        for result in results:
            task = Task.objects.create(
                patient = patient,
                name = name,
                notes = notes,
                date = contact_date,
                follow_up_date = result.date(),
                time_spent = '0',
                task_date = result.date(),
                care_manager = care_manager,
            )
            task.time_spent = datetime.timedelta(minutes=int(task.time_spent))
            task.save()
        return goaltask_obj    
    
class GoalTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalTask
        fields = "__all__"    
