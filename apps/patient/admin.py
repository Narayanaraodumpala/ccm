from django.contrib import admin

from apps.account_manager.models import PatientContactDetails
from apps.patient.models import AnnualWellnessVisitCallLog, AssessmentCallLog, Assistance, GoalChallenges, Intervention, \
    ProgramInformation, BMI, BloodPressure, \
    BloodGlucose, PulseOx, HBA1C, Cholesterol, \
    Notes, \
    Goal, SelfManagementPlanCallLog, StepsToAchieveGoal, Task, MedicationNotes, PatientCallLog, AnnualWellnessVist, \
    ProgramInformationType, ViewLogs, \
    VitalCallLog, MedicalConditionCallLog, PatientOutreach, ScreeningName, Problems, Allergies, Immunization, \
    LabReports, Procedures, PatientDocs, AWVWho, AWVHowOften, ScreeningWhoOften,GeneralNotesCallLog, CareManagerNotes, DailyOutreach, WeeklyOutreach, GoalTask, DailyGoalTask


class AnnualWellnessVistAdmin(admin.ModelAdmin):
    list_display = ('patient', 'date_of_last_services', 'services_and_Screening_name', 'annual_wellness_status')
    search_fields = ('patient__user__first_name',) 


class GoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'patient', 'goal_date', 'goal_status')


class MedicationNotesAdmin(admin.ModelAdmin):
    list_display = ('care_manager', 'patient')
    search_fields = ('patient__user__first_name',)
    
    
class NotesAdmin(admin.ModelAdmin):
    list_display = ('name', 'patient')
    search_fields = ('patient__user__first_name',)
    
    
class PatientCallLogAdmin(admin.ModelAdmin):
    list_display = ('agenda', 'patient', 'care_manager', 'call_start_datetime', 'call_end_datetime', 'call_status', 'call_duration', 'call_type')        
    search_fields = ('patient__user__first_name',)
    
    
class ProgramInformationTypeAdmin(admin.ModelAdmin):
    list_display = ('program_name', )


class ProgramInformationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'program_type', 'date', 'program_status')
    search_fields = ('patient__user__first_name',)


# class TaskAdmin(admin.ModelAdmin):
#     # list_display = ('pk', 'goal', 'intervention', 'patient', 'name', 'care_manager', 'task_date', 'task_status')
#     list_display = ['name']
    # search_fields = ('patient__user__first_name',)


class PatientOutreachAdmin(admin.ModelAdmin):
    list_display = ('patient', 'contact_date', 'schedule_follow_up_date', 'contact_type', 'provider', 'time_spent', 'care_program', 'care_program_from_date', 'care_program_to_date')
    search_fields = ('patient__user__first_name',)


class ProblemsAdmin(admin.ModelAdmin):
    list_display = ('name', 'patient')
    search_fields = ('patient__user__first_name',)


class AllergiesAdmin(admin.ModelAdmin):
    list_display = ('name', 'patient')
    search_fields = ('patient__user__first_name',)


class ImmunizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'patient')
    search_fields = ('patient__user__first_name',)


class LabReportsAdmin(admin.ModelAdmin):
    list_display = ('name', 'patient')
    search_fields = ('patient__user__first_name',)


class ProceduresAdmin(admin.ModelAdmin):
    list_display = ('name', 'patient')
    search_fields = ('patient__user__first_name',)


class PatientDocsAdmin(admin.ModelAdmin):
    list_display = ('name', 'patient')
    search_fields = ('patient__user__first_name',)


class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'patient')
    search_fields = ('name', 'patient__user__first_name',)


admin.site.register(ProgramInformation, ProgramInformationAdmin)
admin.site.register(BMI)
admin.site.register(BloodPressure)
admin.site.register(BloodGlucose)
admin.site.register(PulseOx)
admin.site.register(HBA1C)
admin.site.register(Cholesterol)
admin.site.register(Notes, NotesAdmin)
admin.site.register(PatientContactDetails)
admin.site.register(Goal, GoalAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(MedicationNotes, MedicationNotesAdmin)
admin.site.register(PatientCallLog, PatientCallLogAdmin)
admin.site.register(AnnualWellnessVist, AnnualWellnessVistAdmin)
admin.site.register(StepsToAchieveGoal)
admin.site.register(GoalChallenges)
admin.site.register(Assistance)
admin.site.register(Intervention)
admin.site.register(ProgramInformationType, ProgramInformationTypeAdmin)
admin.site.register(VitalCallLog)
admin.site.register(MedicalConditionCallLog)
admin.site.register(AssessmentCallLog)
admin.site.register(ScreeningName)
admin.site.register(ScreeningWhoOften)
admin.site.register(AnnualWellnessVisitCallLog)
admin.site.register(SelfManagementPlanCallLog)
admin.site.register(PatientOutreach, PatientOutreachAdmin)
admin.site.register(DailyOutreach)
admin.site.register(WeeklyOutreach)

# Default issue model register
admin.site.register(Problems, ProblemsAdmin)
admin.site.register(Allergies, AllergiesAdmin)
admin.site.register(Immunization, ImmunizationAdmin)
admin.site.register(LabReports, LabReportsAdmin)
admin.site.register(Procedures, ProceduresAdmin)
admin.site.register(PatientDocs, PatientDocsAdmin)
admin.site.register(ViewLogs)
admin.site.register(AWVWho)
admin.site.register(AWVHowOften)
admin.site.register(GeneralNotesCallLog)
admin.site.register(CareManagerNotes)
admin.site.register(GoalTask)
admin.site.register(DailyGoalTask)

