import uuid
from django.db import models

from apps.authentication.models import BaseModel, User
from apps.authentication.constants import STATUS

GENDER = (
    ("MALE", "Male"),
    ("FEMALE", "Female"),
    ("OTHER", "Other"),
)


class PracticeAdmin(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    hospital = models.ForeignKey(
        "hospital.Hospital",
        null=True,
        on_delete=models.SET_NULL,
    )
    practice_admin_status = models.CharField(
        max_length=15, choices=STATUS, default="ACTIVE", null=True, blank=True
    )

    def __str__(self):
        return str(self.user)


class Provider(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hospital = models.ForeignKey(
        "hospital.Hospital",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="provider_hospital",
    )
    department = models.ForeignKey(
        "hospital.Department",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="department",
    )
    gender = models.CharField(
        max_length=15, choices=GENDER, null=True, blank=True, default=None
    )
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    npi_data = models.CharField(max_length=225)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    provider_status = models.CharField(
        max_length=15, choices=STATUS, null=True, blank=True, default="ACTIVE"
    )
    taxonomy_description = models.CharField(max_length=225, null=True, blank=True)
    taxonomy_code_set = models.CharField(max_length=225, null=True, blank=True)
    taxonomy_code = models.CharField(max_length=225, null=True, blank=True)
    address_1 = models.CharField(max_length=225, null=True, blank=True)
    address_2 = models.CharField(max_length=225, null=True, blank=True)
    city = models.CharField(max_length=225, null=True, blank=True)
    state = models.CharField(max_length=225, null=True, blank=True)
    zip_code = models.CharField(max_length=225, null=True, blank=True)
    contact_number_two = models.CharField(max_length=20, null=True, blank=True)
    # hospital_branch = models.ForeignKey(
    #     "hospital.HospitalBranch",
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL,
    #     related_name="hospital_branch"
    # )

    def __str__(self):
        return str(self.user)


class CareManager(BaseModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="care_users"
    )
    hospital = models.ForeignKey(
        "hospital.Hospital",
        null=True,
        on_delete=models.SET_NULL,
        related_name="caremanager_info",
    )
    contact = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=225, null=True, blank=True)
    care_manager_status = models.CharField(max_length=15, choices=STATUS, default="ACTIVE", null=True, blank=True)
    # hospital_branch = models.ForeignKey("hospital.HospitalBranch", null=True, on_delete=models.SET_NULL)
    secondary_email = models.EmailField(null=True, blank=True)
    secondary_contact = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return str(self.user)


class Communication(BaseModel):
    communication_type = models.CharField(max_length=225)

    def __str__(self):
        return str(self.communication_type)


class Patient(BaseModel):
    #id = models.BigIntegerField(primary_key=True,unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hospital = models.ForeignKey(
        "hospital.Hospital",
        null=True,
        on_delete=models.SET_NULL,
        related_name="patient_info",
    )
    title = models.CharField(max_length=225, null=True, blank=True)
    middle_name = models.CharField(max_length=225, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=15, choices=GENDER, null=True, blank=True, default=None
    )
    patient_status = models.CharField(
        max_length=15, choices=STATUS, null=True, blank=True, default="ACTIVE"
    )
    caremanager = models.ForeignKey(
        "hospital.HospitalBranch",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="patient_care_manager",
    )
    caremanager_obj = models.ForeignKey(CareManager, null=True, blank=True, on_delete=models.SET_NULL, related_name="patients_care_manager")

    def __str__(self):
        return str(self.user.email)


class PatientProviderMapping(BaseModel):
    patient = models.ForeignKey(
        Patient,
        related_name="patient_patientprovidermapping",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    primary_provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="pri_provider",
    )
    secondary_provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sec_provider",
    )

    def __str__(self) -> str:
        return str(self.patient)


class PatientContactDetails(models.Model):
    patient = models.ForeignKey(
        Patient,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="patient_contact_detail",
    )
    communication = models.ManyToManyField(
        Communication,
        null=True,
        blank=True,
        related_name="communication",
    )
    caremanager = models.ForeignKey(
        CareManager,
        related_name="patient_caremanager",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    secondary_email = models.CharField(max_length=225, null=True, blank=True)
    address_1 = models.CharField(max_length=225, null=True, blank=True)
    address_2 = models.CharField(max_length=225, null=True, blank=True)
    city = models.CharField(max_length=225, null=True, blank=True)
    state = models.CharField(max_length=225, null=True, blank=True)
    zip_code = models.CharField(max_length=225, null=True, blank=True)
    home_phone = models.CharField(max_length=225, null=True, blank=True)
    cell_phone = models.CharField(max_length=225, null=True, blank=True)
    medicare_id = models.CharField(max_length=225, null=True, blank=True)
    medicaid_id = models.CharField(max_length=225, null=True, blank=True)
    primary_insurance = models.CharField(max_length=225, null=True, blank=True)
    primary_insurance_id = models.CharField(max_length=225, null=True, blank=True)
    secondary_insurance = models.CharField(max_length=225, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.patient}"


class PatientSession(BaseModel):
    caremanager = models.ForeignKey(
        CareManager, on_delete=models.CASCADE, null=True, blank=True
    )
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, null=True, blank=True
    )
    duration = models.DurationField(null=True, blank=True)
    session_id = models.CharField(max_length=225, null=True, blank=True)

    def __str__(self):
        return f"{self.patient}"
