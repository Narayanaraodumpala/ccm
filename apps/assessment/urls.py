from django.urls import path
from apps.assessment import views

urlpatterns = [
    path("create/appointment/", views.AppointmentScheduleView.as_view()),
    path("appointment/<int:id>/", views.AppointmentScheduleView.as_view()),
    path("appointment/list/", views.AppointmentListView.as_view()),
    path("self-management/create/", views.SelfManagementPlanView.as_view()),
    path("self-management/details/<int:id>/", views.SelfManagementPlanDetailsView.as_view()),
    path("get/patient/details/<int:pk>/", views.GetPatientDetailsView.as_view()),

    path("question/category/", views.AssessmentQuestionCategoryView.as_view()),  # Get question category list

    path("get/question/", views.AssessmentQuestionListView.as_view()),  # get all questions

    path("get/question/<int:category_id>/", views.GetQuestionView.as_view()),  # Get questions list based on category id
    path("assessment/", views.CreateAssessmentView.as_view()), ## (2)
    path("assessment/<int:patient_id>/", views.GetPatientAssessmentView.as_view()),##(4)
    path("update/assessment/<int:patient_id>/", views.PatientAssessmentUpdateView.as_view()),
    # PatientAssessmentUpdateView

    path("patient/quetion/answer/", views.PatientQuestionAnswerView.as_view()), ## (1)
    path("get/patient/quetion/answer/<int:patient_id>/", views.GetPatientQuestionAnswerView.as_view()),
    path("get/<int:assessment_id>/<int:patient_id>/", views.GetAssessmentPatiantDataView.as_view()), ##(3)
    path("update/answer/<int:question_id>/", views.PatientAnswerUpdateView.as_view()), ##(5)
    path("update/assessment/manual_time/", views.UpdateAssessmentMannualTimeView.as_view()), ##(6)
    

]
