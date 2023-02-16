from django.contrib import admin

from apps.assessment.models import (AppointmentSchedule,SelfManagementPlan, Assessment, 
                                    AssessmentQuestionCategory, QuestionAnswer,Question, 
                                    PatientQuestionAnswer )


class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'question_category', 'start_date', 'end_date', 'date', 'assessment_status',)
    search_fields = ('patient__user__first_name',)


# Register your models here.
admin.site.register(AppointmentSchedule)
admin.site.register(SelfManagementPlan)
admin.site.register(AssessmentQuestionCategory)
admin.site.register(QuestionAnswer)
admin.site.register(Question)
admin.site.register(Assessment, AssessmentAdmin)
admin.site.register(PatientQuestionAnswer)