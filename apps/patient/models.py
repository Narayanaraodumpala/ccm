import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.account_manager.models import CareManager, Provider
from apps.hospital.models import Patient, ChronicCondition
from apps.authentication.models import BaseModel, User


class ProgramInformationType(BaseModel):
    program_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.program_name)


class ProgramInformation(BaseModel):
    PROGRAM_STATUS = (
        ("ACTIVE", "Active"),
        ("DECLINED", "Declined"),
        ("INACTIVE", "Inactive"),
        ("NOTREACHABLE", "NotReachable")
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    program_type = models.ForeignKey(
        ProgramInformationType, on_delete=models.CASCADE, null=True, blank=True
    )
    date = models.DateField(null=True, blank=True)
    program_status = models.CharField(
        max_length=15, choices=PROGRAM_STATUS, null=True, blank=True, default="ACTIVE"
    )

    def __str__(self):
        return str(self.patient)


class ScreeningName(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.name)


class ScreeningWhoOften(BaseModel):
    screening = models.ForeignKey(
        ScreeningName, on_delete=models.CASCADE, null=True, blank=True
    )
    who = models.CharField(max_length=400, null=True, blank=True)
    often = models.CharField(max_length=400, null=True, blank=True)

    def __str__(self):
        return str(self.screening.name)


class AWVWho(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class AWVHowOften(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class AnnualWellnessVist(BaseModel):
    STATUS = (
        ("MET", "Met"),
        ("NOTMET", "Not-Met"),
        ("EXCLUDED", "Excluded"),
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="awv_patient")
    services_and_Screening_name = models.ForeignKey(
        ScreeningName, on_delete=models.CASCADE, blank=True, null=True
    )
    date_of_last_services = models.DateField(null=True, blank=True)
    annual_wellness_status = models.CharField(
        max_length=15, choices=STATUS, null=True, blank=True, default="NOTMET"
    )
    notes = models.CharField(max_length=556, blank=True, null=True)
    who = models.CharField(max_length=556, blank=True, null=True)
    often = models.CharField(max_length=556, blank=True, null=True)
    next_schedule_date = models.CharField(max_length=556, blank=True, null=True)
    need = models.BooleanField(blank=True, null=True)
    completed_by_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.patient)


SOURCE_ENTRIES = (
        ("PATIENT", "Patient"),
        ("EMR", "Emr"),
        ("OTHERS", "Others")
    )
class BMI(BaseModel):
    session_id = models.UUIDField(default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="patient_bmi",
        null=True,
        blank=True,
    )
    date = models.DateField(null=True, blank=True)
    weight = models.CharField(max_length=15, null=True, blank=True)
    unit = models.CharField(max_length=15, null=True, blank=True)  # Kg / Lbs
    height_ft = models.CharField(max_length=10, null=True, blank=True)
    height_inch = models.CharField(max_length=10, null=True, blank=True)
    height = models.CharField(max_length=10, null=True, blank=True)
    bmi_score = models.CharField(max_length=10, null=True, blank=True)
    source_entry = models.CharField(
        max_length=15, choices=SOURCE_ENTRIES, null=True, blank=True
    )

    def __str__(self):
        return str(self.patient.user.email)


class BloodPressure(BaseModel):
    session_id = models.UUIDField(default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        Patient, related_name="patient_blood_pressure", on_delete=models.CASCADE
    )

    date = models.DateField(null=True, blank=True)
    pulse = models.CharField(max_length=10, null=True, blank=True)
    systolic = models.CharField(max_length=10, null=True, blank=True)
    diastolic = models.CharField(max_length=10, null=True, blank=True)
    notes = models.CharField(max_length=550, null=True, blank=True)
    source_entry = models.CharField(
        max_length=15, choices=SOURCE_ENTRIES, null=True, blank=True
    )

    def __str__(self):
        return str(self.patient.user.email)


class BloodGlucose(BaseModel):
    TEST_TYPE = (
        ("FASTING", "Fasting"),
        ("RANDOM", "Random"),
        ("2-HOUR-POST-PRANDIAL", "2-Hour Post Prandial"),
    )
    session_id = models.UUIDField(default=uuid.uuid4, editable=False)
    date = models.DateField(max_length=225, null=True, blank=True)
    test_type = models.CharField(
        max_length=50, choices=TEST_TYPE, null=True, blank=True, default=None
    )
    blood_sugar = models.CharField(max_length=200, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    patient = models.ForeignKey(
        Patient, related_name="patient_blood_glucose", on_delete=models.CASCADE
    )
    source_entry = models.CharField(
        max_length=15, choices=SOURCE_ENTRIES, null=True, blank=True
    )

    def __str__(self):
        return str(self.patient.user.email)


PULSE_STATUS = (("ONE", "one"), ("TWO", "two"))


class PulseOx(BaseModel):
    session_id = models.UUIDField(default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        Patient, related_name="patient_pulseOx", on_delete=models.CASCADE
    )
    date = models.DateField(null=True, blank=True)
    spo2 = models.CharField(max_length=15, choices=PULSE_STATUS, null=True, blank=True)
    pulse_rate = models.CharField(max_length=225)
    notes = models.CharField(max_length=500, null=True, blank=True)
    spo2_value = models.CharField(max_length=15,null=True, blank=True)
    source_entry = models.CharField(
        max_length=15, choices=SOURCE_ENTRIES, null=True, blank=True
    )

    def __str__(self):
        return str(self.patient.user.email)


class Cholesterol(BaseModel):
    session_id = models.UUIDField(default=uuid.uuid4, editable=False)
    date = models.DateField(max_length=225, null=True, blank=True)
    total_cholesterol = models.CharField(max_length=200, null=True, blank=True)
    triglycerides = models.CharField(max_length=200, null=True, blank=True)
    hdl = models.CharField(max_length=200, null=True, blank=True)
    ldl = models.CharField(max_length=200, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    patient = models.ForeignKey(
        Patient, related_name="patient_cholesterol", on_delete=models.CASCADE
    )
    source_entry = models.CharField(
        max_length=15, choices=SOURCE_ENTRIES, null=True, blank=True
    )

    def __str__(self):
        return str(self.patient.user.email)


class HBA1C(BaseModel):
    session_id = models.UUIDField(default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        Patient, related_name="patient_hba1c", on_delete=models.CASCADE
    )
    date = models.DateField(null=True, blank=True)
    hbaic = models.CharField(max_length=225)
    notes = models.CharField(max_length=500, null=True, blank=True)
    source_entry = models.CharField(
        max_length=15, choices=SOURCE_ENTRIES, null=True, blank=True
    )

    def __str__(self):
        return str(self.patient.user.email)


class Notes(BaseModel):
    name = models.CharField(max_length=225, null=True, blank=True)
    description = models.TextField()
    file_field = models.FileField(upload_to="vitals-files/", null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.patient.user.email)


STATUS = (("PENDING", "Pending"), ("COMPLETED", "Completed"))


SCORE = (
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4", "4"),
    ("5", "5"),
    ("6", "6"),
    ("7", "7"),
    ("8", "8"),
    ("9", "9"),
    ("10", "10"),
)


class Goal(BaseModel):
    name = models.CharField(max_length=225, null=True, blank=True)
    goal_date = models.DateTimeField(null=True, blank=True)
    goal_status = models.CharField(
        max_length=15, choices=STATUS, null=True, blank=True, default="ACTIVE"
    )
    notes = models.TextField(null=True, blank=True)
    patient_refused = models.BooleanField(null=True, blank=True)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="patient_goal",
    )
    chronic_condition = models.ForeignKey(
        ChronicCondition, on_delete=models.CASCADE, null=True, blank=True
    )

    #
    # steps_to_achieve_goal = models.CharField(max_length=255, null=True, blank=True)
    # steps_to_achieve_goal_score = models.CharField(max_length=255, null=True, blank=True)
    #
    # goal_challenges_issue = models.CharField(max_length=255, null=True, blank=True)
    # goal_challenges_score = models.CharField(max_length=255, null=True, blank=True)
    #
    # assistance_type = models.CharField(max_length=255, null=True, blank=True)
    # assistance_score = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.name)


class StepsToAchieveGoal(BaseModel):
    goal_plan = models.CharField(max_length=200, null=True, blank=True)
    score = models.CharField(
        max_length=15, choices=SCORE, null=True, blank=True, default=None
    )
    goal = models.ForeignKey(
        Goal,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="steps_to_achieve_goal",
    )

    def __str__(self):
        return self.goal_plan


class GoalChallenges(BaseModel):
    challenges = models.CharField(max_length=200, null=True, blank=True)
    score = models.CharField(
        max_length=15, choices=SCORE, null=True, blank=True, default=None
    )
    goal = models.ForeignKey(
        Goal,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="challenge_goal",
    )

    def __str__(self):
        return f"{self.pk}"


class Assistance(BaseModel):
    support_type = models.CharField(max_length=200, null=True, blank=True)
    score = models.CharField(
        max_length=15, choices=SCORE, null=True, blank=True, default=None
    )
    goal = models.ForeignKey(
        Goal,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="assistance_goal",
    )

    def __str__(self):
        return self.support_type


INTERVENTION_STATUS = (
    ("PENDING", "Pending"),
    ("COMPLETED", "Completed"),
    
)


class Intervention(BaseModel):
    name = models.CharField(max_length=50, null=True, blank=True, default=None)
    date = models.DateTimeField(max_length=50, null=True, blank=True, default=None)
    status = models.CharField(
        max_length=15,
        choices=INTERVENTION_STATUS,
        null=True,
        blank=True,
        default="PENDING",
    )
    notes = models.CharField(max_length=200, null=True, blank=True)
    recurrence_pattern = models.CharField(max_length=55, null=True, blank=True)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, null=True, blank=True)


TASK_RESOLUTION_ACTION = (
    ("LEFT-MESSAGE", "Left Message"),
    ("CALLBACK-LATER", "Call Back Later"),
    ("OTHER", "Other"),
    ("DECLINED", "Declined"),
    ("NOT-REACHABLE", "Not Reachable"),
)


class Task(BaseModel):
    notes = models.TextField(max_length=225, null=True, blank=True)  # 1
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, null=True, blank=True
    )  # 1
    care_manager = models.ForeignKey(
        CareManager, on_delete=models.CASCADE, null=True, blank=True
    )  # 1
    task_status = models.CharField(
        max_length=15, choices=STATUS, null=True, blank=True, default="PENDING"
    )  # 1
    date = models.DateField(null=True, blank=True)
    # recurrence_pattern = models.CharField(max_length=255, null=True, blank=True)
    time_spent = models.DurationField(null=True, blank=True)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)

    goal = models.ForeignKey(
        Goal, on_delete=models.CASCADE, related_name="goal", null=True, blank=True
    )
    intervention = models.ForeignKey(
        Intervention,
        on_delete=models.CASCADE,
        related_name="intervention",
        null=True,
        blank=True,
    )
    task_date = models.DateField(
        null=True, blank=True
    )  # Same as goal/intervention date
    # For standalone task
    name = models.CharField(max_length=255, null=True, blank=True)
    is_self_task = models.BooleanField(default=False, null=True, blank=True)
    resolution_action = models.CharField(
        max_length=255,
        choices=TASK_RESOLUTION_ACTION,
        null=True,
        blank=True,
        default=None,
    )
    follow_up_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.patient)


class MedicationNotes(BaseModel):
    care_manager = models.ForeignKey(
        CareManager, on_delete=models.CASCADE, null=True, blank=True
    )
    description = models.TextField()
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.patient.user.email)


CALL_STATUS = (
    ("IN-PROGRESS", "In Progress"),
    ("COMPLETED", "Completed"),
)

CALL_TYPES = (
    ("CALL-DECLINED", "Call Declined"),
    ("COMPLETED", "Completed"),
    ("NOT-QUALIFIED", "Not Qualified"),
    ("VOICE-MAIL", "Voice Mail"),
    ("AUDIO-CALL", "Audio Call"),
    ("OTHERS", "Others"),
)


class PatientCallLog(BaseModel):
    agenda = models.CharField(max_length=225, null=True, blank=True)
    recording = models.FileField(upload_to="call-recording/", null=True, blank=True)
    call_meet_link = models.CharField(
        max_length=255, unique=True, null=True, blank=True
    )
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="patient_patientcall_log"
    )
    care_manager = models.ForeignKey(
        CareManager, on_delete=models.CASCADE, null=True, blank=True
    )
    call_start_datetime = models.DateTimeField(null=True, blank=True)
    call_end_datetime = models.DateTimeField(null=True, blank=True)
    call_duration = models.DurationField(null=True, blank=True)
    call_status = models.CharField(
        max_length=15, choices=CALL_STATUS, null=True, blank=True, default="IN-PROGRESS"
    )
    call_type = models.CharField(
        max_length=15, choices=CALL_TYPES, null=True, blank=True, default="AUDIO-CALL"
    )

    def __str__(self):
        return str(self.patient.user.email)


class VitalCallLog(BaseModel):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="patient_vitalcall_log",
    )
    care_manager = models.ForeignKey(
        CareManager, on_delete=models.CASCADE, null=True, blank=True
    )
    call_duration = models.DurationField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.patient)


class MedicalConditionCallLog(BaseModel):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="patient_medicalconditioncalllog",
    )
    care_manager = models.ForeignKey(
        CareManager, on_delete=models.CASCADE, null=True, blank=True
    )
    call_duration = models.DurationField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.patient)


class AssessmentCallLog(BaseModel):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="patient_assessmentcalllog",
    )
    care_manager = models.ForeignKey(
        CareManager, on_delete=models.CASCADE, null=True, blank=True
    )
    call_duration = models.DurationField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.patient)


class AnnualWellnessVisitCallLog(BaseModel):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="patient_annualwellnessvisit_calllog",
    )
    care_manager = models.ForeignKey(
        CareManager, on_delete=models.CASCADE, null=True, blank=True
    )
    call_duration = models.DurationField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.patient)


class SelfManagementPlanCallLog(BaseModel):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="patient_selfmanagementplancalllog",
    )
    care_manager = models.ForeignKey(
        CareManager, on_delete=models.CASCADE, null=True, blank=True
    )
    call_duration = models.DurationField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.patient)


PATIENT_OUTREACH_STATUS = (
    ("CALL-DECLINED", "Call Declined"),
    ("COMPLETED", "completed"),
    ("NOT-QUALIFIED", "Not Qualified"),
    ("VOICE-MAIL", "Voice Mail"),
    ("OUTREACH", "Outreach"),
    ("OTHERS", "others"),
)

 
CONTACT_TYPE = (
    ("CARE-PLAN-CREATION", "Care Plan Creation"),
    ("CARE-PLAN-DISCUSSION", "Care Plan Discussion"),
    ("CARE-PLAN-REVISION", "Care Plan Revision"),
    ("CLINICAL-ASSESSMENTS", "Clinical Assessments"),
    ("EMAIL", "Email"),
    ("MAILERS", "Mailers (Assessments  / Education)"),
    ("MONTHLY-CLINICAL-REVIEW", "Monthly clinical review"),
    ("OTHER", "Other"),
    ("OTHER-PROVIDER/CARE-GIVERS", "Other providers / Care givers"),
    ("REFERRALS", "Referrals"),    
    ("SCHEDULED-APPOINTMENT", "Scheduled Appointment"),    
    ("TELEPHONE-CALL", "Telephone Call"),
)
RESOLUTION_ACTION = (
    ("CALLBACK-LATER", "Callback Later"),
    ("COMPLETED", "Completed"),
    ("DECLINED", "Declined"),
    ("NOT-REACHABLE", "Not Reachable"),
    ("NOT-QUALIFIED", "Not Qualified"),
    ("OTHER", "Other"),
    ("VOICE-MESSAGE", "Voice-Message"),
)
OUTCOME = (
    ("COMPLETED", "Completed"),
    ("CALL-DECLINED", "Call Declined"),
    ("NOT-QUALIFIED", "Not Qualified"),
    ("VOICE-MAIL", "Voice Mail"),
    ("OTHER", "Other"),
)
OUTREACH_STATUS = (
    ("COMPLETED", "Completed"),
    ("PENDING", "Pending"),
    ("ABUNDANT", "Abundant"),
)


class PatientOutreach(BaseModel):
    outreach_name = models.CharField(max_length=255, null=True, blank=True)
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, null=True, blank=True
    )
    contact_date = models.DateField(null=True, blank=True)
    schedule_follow_up_date = models.DateField(null=True, blank=True)
    contact_type = models.CharField(
        max_length=55, choices=CONTACT_TYPE, null=True, blank=True, default=None
    )
    resolution_action = models.CharField(
        max_length=255, choices=RESOLUTION_ACTION, null=True, blank=True, default=None
    )
    outcome = models.CharField(
        max_length=255, choices=OUTCOME, null=True, blank=True, default=None
    )
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, null=True, blank=True
    )
    time_spent = models.DurationField(null=True, blank=True)
    notes = models.TextField(max_length=1225, null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    # Time Period of care program
    care_program = models.CharField(max_length=55, null=True, blank=True)
    care_program_from_date = models.DateField(null=True, blank=True)
    care_program_to_date = models.DateField(null=True, blank=True)

    care_member = models.CharField(max_length=255, null=True, blank=True)
    patientoutreach_status = models.CharField(
        max_length=15,
        choices=PATIENT_OUTREACH_STATUS,
        null=True,
        blank=True,
        default="COMPLETED",
    )
    outreach_status = models.CharField(
        max_length=15, choices=OUTREACH_STATUS, null=True, blank=True, default="PENDING"
    )
    care_manager = models.ForeignKey(
        CareManager, on_delete=models.CASCADE, null=True, blank=True
    )
    recurrence_pattern = models.BooleanField(blank=True, null=True, default=False)
    daily = models.OneToOneField("DailyOutreach", on_delete=models.CASCADE, blank=True, null=True)
    weekly = models.OneToOneField("WeeklyOutreach", on_delete=models.CASCADE, blank=True, null=True)
    bi_weekly = models.BooleanField(blank=True, null=True, default=False)
    monthly = models.BooleanField(blank=True, null=True, default=False)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)

    def __str__(self):
        # if str(self.patient):
        #     return str(self.patient.user.email)
        return str(self.outcome)


class DailyOutreach(BaseModel):
    weekday = models.BooleanField(blank=True, null=True, default=False)
    weekend = models.BooleanField(blank=True, null=True, default=False)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)

    # def __str__(self):
    #     return self.weekday


class WeeklyOutreach(BaseModel):
    sunday = models.BooleanField(blank=True, null=True, default=False)
    monday = models.BooleanField(blank=True, null=True, default=False)
    tuesday = models.BooleanField(blank=True, null=True, default=False)
    wednesday = models.BooleanField(blank=True, null=True, default=False)
    thursday = models.BooleanField(blank=True, null=True, default=False)
    friday = models.BooleanField(blank=True, null=True, default=False)
    saturday = models.BooleanField(blank=True, null=True, default=False)


# Default Problems/Issues
class Problems(BaseModel):
    name = models.CharField(max_length=225, null=True, blank=True)
    description = models.TextField()
    file_field = models.FileField(
        upload_to="default-issues-files/", null=True, blank=True
    )
    patient = models.ForeignKey(Patient, related_name="patient_problems",on_delete=models.CASCADE)
    source_entry = models.CharField(
        max_length=15, choices=SOURCE_ENTRIES, null=True, blank=True
    )

    def __str__(self):
        return str(self.patient.user.email)


SOURCE_ENTRIES = (
        ("PATIENT", "Patient"),
        ("EMR", "Emr"),
        ("OTHERS", "Others")
    )

class Allergies(BaseModel):
    name = models.CharField(max_length=225, null=True, blank=True)
    description = models.TextField()
    file_field = models.FileField(
        upload_to="default-issues-files/", null=True, blank=True
    )
    patient = models.ForeignKey(Patient, related_name="patient_allergies", on_delete=models.CASCADE)
    source_entry = models.CharField(
        max_length=115, choices=SOURCE_ENTRIES, null=True, blank=True
    )

    def __str__(self):
        return str(self.patient.user.email)


class Immunization(BaseModel):
    name = models.CharField(max_length=225, null=True, blank=True)
    description = models.TextField()
    file_field = models.FileField(
        upload_to="default-issues-files/", null=True, blank=True
    )
    patient = models.ForeignKey(Patient, related_name="patient_immunization",on_delete=models.CASCADE)
    physician_name = models.CharField(max_length=225, null=True, blank=True)
    source_entry = models.CharField(
        max_length=115, choices=SOURCE_ENTRIES, null=True, blank=True
    )

    def __str__(self):
        return str(self.patient.user.email)


class LabReports(BaseModel):
    name = models.CharField(max_length=225, null=True, blank=True)
    description = models.TextField()
    file_field = models.FileField(
        upload_to="default-issues-files/", null=True, blank=True
    )
    patient = models.ForeignKey(Patient,related_name="patient_labreport", on_delete=models.CASCADE)
    source_entry = models.CharField(
        max_length=15, choices=SOURCE_ENTRIES, null=True, blank=True
    )

    def __str__(self):
        return str(self.patient.user.email)


class Procedures(BaseModel):
    name = models.CharField(max_length=225, null=True, blank=True)
    description = models.TextField()
    file_field = models.FileField(
        upload_to="default-issues-files/", null=True, blank=True
    )
    patient = models.ForeignKey(Patient,related_name="patient_procedures",on_delete=models.CASCADE)
    hospital = models.CharField(max_length=225, null=True, blank=True)
    source_entry = models.CharField(
        max_length=15, choices=SOURCE_ENTRIES, null=True, blank=True
    )

    def __str__(self):
        return str(self.patient.user.email)


class PatientDocs(BaseModel):
    name = models.CharField(max_length=225, null=True, blank=True)
    description = models.TextField()
    file_field = models.FileField(
        upload_to="default-issues-files/", null=True, blank=True
    )
    patient = models.ForeignKey(Patient,related_name="patient_docs", on_delete=models.CASCADE)
    source_entry = models.CharField(
        max_length=15, choices=SOURCE_ENTRIES, null=True, blank=True
    )

    def __str__(self):
        return str(self.patient.user.email)


class ViewLogs(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return str(self.user.email)


class GeneralNotesCallLog(BaseModel):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="patient_general_notescall_log",
    )
    care_manager = models.ForeignKey(
        CareManager, on_delete=models.CASCADE, null=True, blank=True
    )
    call_duration = models.DurationField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.patient)


CM_Notes_STATUS = (
    ("COMPLETED", "Completed"),
    ("PENDING", "Pending"),
)


class CareManagerNotes(BaseModel):
    chronic_condition = models.CharField(max_length=225, null=True, blank=True)
    time_spent = models.DurationField(null=True, blank=True)
    notes = models.CharField(max_length=225, null=True, blank=True)
    cm_notes_status = models.CharField(
        max_length=15, choices=CM_Notes_STATUS, null=True, blank=True
    )
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, null=True, blank=True
    )
    care_manager = models.ForeignKey(
        CareManager, on_delete=models.CASCADE, null=True, blank=True
    )
    caremanager_notes_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.chronic_condition)


class DailyGoalTask(BaseModel):
    weekday = models.BooleanField(blank=True, null=True, default=False)
    weekend = models.BooleanField(blank=True, null=True, default=False)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)

GoalTask_STATUS = (
    ("PENDING", "Pending"),
    ("COMPLETED", "Completed"),
    
)    
    
class GoalTask(BaseModel):
    name = models.CharField(max_length=50, null=True, blank=True, default=None)
    date = models.DateTimeField(max_length=50, null=True, blank=True, default=None)
    status = models.CharField(
        max_length=15,
        choices=GoalTask_STATUS,
        null=True,
        blank=True,
        default="PENDING",
    )
    contact_type = models.CharField(
        max_length=55, choices=CONTACT_TYPE, null=True, blank=True, default=None
    )
    notes = models.CharField(max_length=200, null=True, blank=True)
    recurrence_pattern = models.CharField(max_length=55, null=True, blank=True)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, null=True, blank=True)
    daily = models.OneToOneField(DailyGoalTask, on_delete=models.CASCADE, blank=True, null=True) 
    time_spent = models.DurationField(null=True, blank=True)
    schedule_follow_up_date = models.DateField(null=True, blank=True)
            
    def __str__(self):
        return self.contact_type
 