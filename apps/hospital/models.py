from django.db import models

from apps.authentication.models import BaseModel
from apps.account_manager.models import Provider, Patient, CareManager
from apps.authentication.constants import STATUS


class Appointment(BaseModel):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    description = models.TextField()
    schedule = models.DateTimeField(auto_now=True)


class DoctorRating(BaseModel):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)


STATUS = (
    ("ACTIVE", "Active"),
    ("INACTIVE", "In-Active"),
    ("SUSPENDED", "Suspended"),
)
class Hospital(BaseModel):
    npi_id = models.CharField(max_length=200, blank=False)
    hospital_name = models.CharField(max_length=200, blank=False)
    hospital_tax_id = models.CharField(max_length=200,  null=True, blank=True)
    contact_person_name = models.CharField(max_length=100)
    email_id = models.EmailField(max_length=100,  null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    address_1 = models.CharField(max_length=500)
    address_2 = models.CharField(max_length=500, null=True, blank=True)
    state_province_area = models.CharField(max_length=200)
    zip_code = models.IntegerField()
    city = models.CharField(max_length=100)
    multiple_branch = models.BooleanField(default=False)
    website_url = models.CharField(max_length=200, null=True, blank=True)
    hospital_status = models.CharField(max_length=15, choices=STATUS, null=True, blank=True, default="ACTIVE")
    hospital_image = models.ImageField(upload_to="media/", null=True, blank=True)
    taxonomy_id = models.CharField(max_length = 200, null=True, blank=True)
    taxonomy_description = models.CharField(max_length=225, null=True, blank=True)

    def __str__(self):
        return self.hospital_name


class HospitalBranch(BaseModel):
    hospital = models.ForeignKey(
        Hospital, related_name="hospital_branch", on_delete=models.CASCADE,null=True, blank=True
    )
    branch_name = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    contact_email = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=100, blank=True, null=True)
    hospital_branch_status = models.CharField(max_length=15, choices=STATUS, default="ACTIVE", null=True, blank=True)
    provider = models.ForeignKey(
        Provider,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="hospital_branch_provider"
    )
    care_manager = models.ForeignKey(
        CareManager,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="hospital_branch_care_manager"

    )

    def __str__(self) -> str:
        return self.branch_name

    # def __str__(self):
    #     if self.care_manager:
    #         return str(self.care_manager)
    #     else: 
    #         return str(self.branch_name)


class Department(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Treatment(BaseModel):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE,related_name="patient_treatment")
    disease_name = models.CharField(max_length=100, blank=False)
    treatment_start_date = models.DateTimeField(null=True)
    medications = models.CharField(max_length=500, blank=False)

    def __str__(self):
        return self.disease_name


class ChronicCondition(BaseModel):
    disease_name = models.CharField(max_length=150, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.disease_name}"


class PatientChronicDisease(BaseModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="chronic_patient")
    chronic = models.ForeignKey(ChronicCondition, on_delete=models.CASCADE, related_name="chronic_disease")
    name = models.CharField(max_length=150, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to="patient-chronic-files/", null=True, blank=True)

    def __str__(self) -> str:
        return self.patient.user.email

class NPI(BaseModel):
    npi_id = models.CharField(max_length=500, null=True, blank=True)
    endpoint_type = models.CharField(max_length=500, null=True, blank=True)
    endpoint_type_description = models.CharField(max_length=500, null=True, blank=True)
    endpoint = models.CharField(max_length=500, null=True, blank=True)
    affiliation = models.CharField(max_length=500, null=True, blank=True)
    endpoint_description = models.CharField(max_length=500, null=True, blank=True)
    affiliation_legal_business_name = models.CharField(max_length=500, null=True, blank=True)
    use_code = models.CharField(max_length=500, null=True, blank=True)
    use_description = models.CharField(max_length=500, null=True, blank=True)
    other_use_description = models.CharField(max_length=500, null=True, blank=True)
    content_type = models.CharField(max_length=500, null=True, blank=True)
    content_description = models.CharField(max_length=500, null=True, blank=True)
    other_content_description = models.CharField(max_length=500, null=True, blank=True)
    affiliation_address_line_one = models.CharField(max_length=500, null=True, blank=True)
    affiliation_address_line_two = models.CharField(max_length=500, null=True, blank=True)
    affiliation_address_city = models.CharField(max_length=500, null=True, blank=True)
    affiliation_address_state = models.CharField(max_length=500, null=True, blank=True)
    affiliation_address_country = models.CharField(max_length=500, null=True, blank=True)
    affiliation_address_postal_code = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.npi_id


CATEGORY = (
    ("INJECTIONS", "injections"),
    ("CAPSULES", "capsules"),
    ("TABLET", "tablet"),
    ("SYRUP", "syrup"),
    
)

FREQUENCY = (
    ("DAILY", "daily"),
    ("WEEKLY", "weekly"),
    ("MONTHLY", "monthly"),
    ("Once a day", "Once a day"),
    ("As Needed", "As Needed"),
    ("Twice a day", "Twice a day"),
    ("Three times a day", "Three times a day"),
    ("Others", "Others"),
)

STATUS = (
    ("ACTIVE", "active"),
    ("INACTIVE", "in-active"),
    ("SUSPENDED", "suspended"),
)

TYPE = (
    ("FEVER", "fever"),
    ("COLD", "cold"),
    ("COUGH", "cough"),
)


class MedicationChronicCondition(BaseModel):
    disease_name = models.CharField(max_length=150, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.disease_name}"

class Medication(BaseModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="patient_medication", null=True, blank=True)
    chronic_condition = models.ForeignKey(MedicationChronicCondition, on_delete=models.CASCADE, null=True,
                                blank=True)
    medication_name = models.CharField(max_length=200)
    category = models.CharField(
        max_length=15, choices=CATEGORY, null=True, blank=True, default=None
    )
    frequency = models.CharField(
        max_length=225, choices=FREQUENCY, null=True, blank=True, default=None
    )
    midication_status = models.CharField(
        max_length=15, choices=STATUS, null=True, blank=True, default=None
    )
    dose = models.CharField(max_length=50,null=True, blank=True)
    type = models.CharField(
        max_length=15, choices=TYPE, null=True, blank=True, default=None
    )
    prescriber = models.CharField(max_length= 225, null=True, blank=True)
    reasons = models.CharField(max_length=225,null=True, blank=True)

    def __str__(self):
        return self.medication_name


class NPITaxonomy(BaseModel):
    medicare_specialty_code = models.CharField(max_length=150, null=True, blank=True)
    medicare_provider_supplier_type_description = models.CharField(max_length=150, null=True, blank=True)
    provider_taxonomy_code = models.CharField(max_length=150, null=True, blank=True)
    provider_taxonomy_description = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return str(self.provider_taxonomy_code)
