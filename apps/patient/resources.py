from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from apps.account_manager.models import Patient, Provider, PatientContactDetails, CareManager
from apps.authentication.models import User
from apps.hospital.models import Hospital, Medication
from apps.patient.models import PatientOutreach, Procedures, Immunization, Allergies, Problems, Goal, GoalTask, Intervention
from apps.account_manager.models import Patient

# class PatientOutreachResource(resources.ModelResource):
#     school_id = fields.Field(
#         column_name='patient',
#         attribute='patient',
#         widget=ForeignKeyWidget(Patient, 'patient'))
#
#     class Meta:
#         model = Patient
#

from import_export import resources
from apps.account_manager.models import Patient


class UserResource(resources.ModelResource):
    class Meta:
        model = User


class PatientResource(resources.ModelResource):
    class Meta:
        model = Patient

# class AttendanceResource(resources.ModelResource):
#     class Meta:
#         model = Attendance


class HospitalResource(resources.ModelResource):
    class Meta:
        model = Hospital
        

class CareManagerResource(resources.ModelResource):
    class Meta:
        model = CareManager
        

class PatientContactDetailsResource(resources.ModelResource):
    class Meta:
        model = PatientContactDetails
        

class ContactandOutreachResource(resources.ModelResource):
    class Meta:
        model = PatientOutreach


class ProviderResource(resources.ModelResource):
    class Meta:
        model = Provider


class GoalTaskResource(resources.ModelResource):
    class Meta:
        model = GoalTask
        
class InterventionResource(resources.ModelResource):
    class Meta:
        model = Intervention        
        

class GoalResource(resources.ModelResource):
    class Meta:
        model = Goal


class ProblemsResource(resources.ModelResource):
    class Meta:
        model = Problems
        

class AllergiesResource(resources.ModelResource):
    class Meta:
        model = Allergies
        

class MedicationsResource(resources.ModelResource):
    class Meta:
        model = Medication
        

class ImmunizationResource(resources.ModelResource):
    class Meta:
        model = Immunization
        

class ProceduresResource(resources.ModelResource):
    class Meta:
        model = Procedures