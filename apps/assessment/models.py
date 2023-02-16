from django.db import models

from apps.hospital.models import Patient
from apps.authentication.models import BaseModel
from apps.patient.models import Task

# Create your models here.
# class SelfManagementPlan(BaseModel):
#     note = models.CharField(max_length=200, null=True, blank=True)
#     description = models.CharField(max_length=200, null=True, blank=True)
#     pdf_file = models.FileField(upload_to="pdfs/", null=True, blank=True)
#     patient = models.ForeignKey(
#         Patient, related_name="patient", on_delete=models.CASCADE
#     )
#     end_date = models.DateTimeField(null=True, blank=True)

#     def __str__(self):
#         return self.note

STATUS = (
    ("PENDING", "pending"),
    ("COMPLETED", "completed")
)

TASK_STATUS = (
    ("PENDING", "pending"),
    ("COMPLETED", "complete"),
    ("ABUNDANT", "abundant")
)


class SelfManagementPlan(BaseModel):
    note = models.CharField(max_length=200, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    # pdf_file = models.FileField(upload_to="pdfs/", null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    task_name = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name="task_name_smp")
    type = models.CharField(max_length=200, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=15, choices=STATUS, null=True, blank=True, default=None
    )
    patient = models.ForeignKey(
        Patient, related_name="patient", on_delete=models.CASCADE, null=True, blank=True
    )
    task_status = models.CharField(
        max_length=15, choices=STATUS, null=True, blank=True, default=None
    )

    def __str__(self):
        return str(self.task_name)


class AppointmentSchedule(BaseModel):
    patient_name = models.CharField(max_length=40)
    appointment_date_time = models.DateTimeField(null=True, blank=True)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.patient_name


class QuestionAnswer(BaseModel):
    questions = models.ForeignKey("Question", on_delete=models.CASCADE)
    answer = models.TextField()

    def __str__(self):
        return str(self.answer)


class AssessmentQuestionCategory(BaseModel):
    question_category = models.TextField()

    def __str__(self):
        return str(self.question_category)


Question_Type = (
    ("YES_NO", "Yes_No"),
    ("SINGLE_SELECT", "Single_Select"),
    ("MULTI_SELECT", "Multi_Select"),
)

class Question(BaseModel):
    question_category = models.ForeignKey(
        AssessmentQuestionCategory, related_name="question_category_info", on_delete=models.CASCADE
    )
    inquiry = models.TextField()
    question_type = models.CharField(
        max_length=15, choices=Question_Type, null=True, blank=True, default=None
    )
    option_1 = models.TextField(null=True, blank=True)
    option_2 = models.TextField(null=True, blank=True)
    option_3 = models.TextField(null=True, blank=True)
    option_4 = models.TextField(null=True, blank=True)
    option_5 = models.TextField(null=True, blank=True)
    ask = models.CharField(max_length=225,null=True, blank=True)
    ask_description = models.TextField(null=True, blank=True)
      
    def __str__(self):
        return str(self.question_category)


ASSESSMENT_STATUS = (
    ("COMPLETED", "Completed"),
    ("PENDING", "Pending"),
)


class Assessment(BaseModel):
    question_category = models.ForeignKey(
        AssessmentQuestionCategory, related_name="assessment_category_info", on_delete=models.CASCADE
    )
    # question = models.ForeignKey(Question, related_name="question", on_delete=models.CASCADE)
    # answer = models.TextField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    date = models.DateField()
    score = models.CharField(max_length=225, null=True, blank=True)
    assessment_status = models.CharField(
        max_length=15, choices=ASSESSMENT_STATUS, null=True, blank=True, default="PENDING"
    )
    time_spent = models.DurationField(null=True, blank=True)
    patient = models.ForeignKey(Patient,
                                related_name='patient_assessment',
                                on_delete=models.CASCADE, null=True, blank=True)
    action_taken = models.CharField(max_length=225, null=True, blank=True)
    manual_time = models.DurationField(null=True, blank=True)
    severity = models.CharField(max_length=225, null=True, blank=True)
    

    def __str__(self):
        return str(self.score)


class PatientQuestionAnswer(BaseModel):
    assessment = models.ForeignKey(
        Assessment, related_name="patient_quetion_answer_assessment", on_delete=models.CASCADE, null=True, blank=True
    )
    patient = models.ForeignKey(Patient, related_name="patient_info", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name="patient_question", on_delete=models.CASCADE, null=True, blank=True)
    answer = models.CharField(max_length=225)
    
    def __str__(self):
        return str(self.answer)
    
    

       
