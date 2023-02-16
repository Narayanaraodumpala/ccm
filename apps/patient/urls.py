from django.urls import path
from apps.patient import views

urlpatterns = [
    path("", views.PatientView.as_view(), name="patient"),
    path("detail/<int:pk>/", views.PatientDetailView.as_view()),
    path(
        "communication/create/",
        views.CommunicationCreateApiView.as_view(),
        name="communication-create",
    ),
    path(
        "communication/retrive/<int:id>/",
        views.CommunicationRetriveApiView.as_view(),
        name="retrieve-communication",
    ),
    path("patient_provider/", views.PatientProviderMappingAPIView.as_view()),
    path("upload_patient_data/", views.UploadPatientDataAPIView.as_view()),

    # Program Information
    path("program/information/", views.ProgramInformationCreateView.as_view()),
    path("program/information/<int:patient_id>/", views.ProgramInformationView.as_view()),
    
    path("program/information/<int:patient_id>/<int:program_info_id>/", views.ProgramInformationUpdateView.as_view()),
    path("program/information/type/", views.ProgramInformationTypeView.as_view()),

    path("goaltask/create/", views.GoalTaskView.as_view()),
    path("intervention/details/<int:id>/", views.GoalTaskDetailsView.as_view()),

    path("show/patient/stats/", views.ShowPatientStatsView.as_view()),
    path("care_manager/overview/patient-task/", views.CareManagerDashboardDetailView.as_view()),
    path("annual-wellness-visit/<int:patient_id>/", views.AnnualWellnessVisitView.as_view()),
    path("annual-wellness-visit/get/<int:patient_id>/", views.AnnualWellnessVisitDetailsView.as_view()),
    path("annual-wellness-visit/put/<int:patient_id>/", views.AnnualWellnessVisitUpdateView.as_view()),
    path("patient/key/stats/<int:pk>/", views.PatientKeyStatAPIView.as_view()),
    path("patient/treatment/communication/<int:pk>/", views.PatientTreatmentCommunicationView.as_view()),
    path("providers-patient-list/<int:id>/", views.ProviderPatientListView.as_view()),
    path("providers-stats-list/<int:pk>/", views.ProviderStatsView.as_view()),
    path("appointments/providers/count/<int:pk>/", views.GetappointmentsProviderCountView.as_view()),
    path("assigned-providers-patient/<int:pk>/", views.ProviderAssignedPatientView.as_view()),

    # Vitals
    path("bmi/", views.BMICreateView.as_view()),
    path("bmi/<int:patient_id>/", views.BMIListView.as_view()),
    path("bmi/all/<int:patient_id>/", views.AllBMIListView.as_view()),
    path("bmi/<int:pk>/<int:patient_id>/", views.BMIUpdateView.as_view()),
    
    path("blood_pressure/", views.BloodPressureCreateView.as_view()),
    path("blood_pressure/<int:patient_id>/", views.BloodPressureListView.as_view()),
    path("blood_pressure/all/<int:patient_id>/", views.AllBloodPressureListView.as_view()),
    path("blood_pressure/<int:pk>/<int:patient_id>/", views.BloodPressureUpdateView.as_view()),
    
    path("blood_glucose/", views.BloodGlucoseCreateView.as_view()),
    path("blood_glucose/<int:patient_id>/", views.BloodGlucoseListView.as_view()),
    path("blood_glucose/all/<int:patient_id>/", views.AllBloodGlucoseListView.as_view()),
    path("blood_glucose/<int:pk>/<int:patient_id>/", views.BloodGlucoseUpdateView.as_view()),
    
    path("pulse_ox/", views.PulseOxCreateView.as_view()),
    path("pulse_ox/<int:patient_id>/", views.PulseOxListView.as_view()),
    path("pulse_ox/all/<int:patient_id>/", views.AllPulseOxListView.as_view()),
    path("pulse_ox/<int:pk>/<int:patient_id>/", views.PulseOxUpdateView.as_view()),
    
    path("hba1c/", views.HBA1CCreateView.as_view()),
    path("hba1c/<int:patient_id>/", views.HBA1CListView.as_view()),
    path("hba1c/all/<int:patient_id>/", views.AllHBA1CListView.as_view()),
    path("hba1c/<int:pk>/<int:patient_id>/", views.HBA1CUpdateView.as_view()),
    
    path("cholesterol/", views.CholesterolCreateView.as_view()),
    path("cholesterol/<int:patient_id>/", views.CholesterolListView.as_view()),
    path("cholesterol/all/<int:patient_id>/", views.AllCholesterolListView.as_view()),
    path("cholesterol/<int:pk>/<int:patient_id>/", views.CholesterolUpdateView.as_view()),

    path("notes/", views.NotesCreateView.as_view()),
    path("notes/<int:patient_id>/", views.NotesListView.as_view()),
    path("goal/", views.GoalView.as_view()),
    path("get/patient/goal/<int:pk>/", views.GetPatientGoalView.as_view()),
    path("get/patient/goal/<int:patient_id>/<int:goal_id>/", views.GetPatientGoalDetailView.as_view()),
    path("task/", views.CreatePatientTaskView.as_view()),
    path("get/patient/task/<int:pk>/", views.GetPatientTaskView.as_view()),
    path("patient-contact-details/<int:patient_id>/", views.PatientContactDetailListView.as_view()),
    path("vitals-details/<int:patient_id>/", views.PatientVitalGlobalSearch.as_view()),

    # Care Manager medications section for patient
    path("medication-notes/", views.MedicationNotesView.as_view()),
    path("medication-notes/<int:patient_id>/", views.MedicationNotesDetailView.as_view()),

    path("create/patient-for-caremanager/", views.CreatePatientforCaremanagerView.as_view()),
    path("create/patient-for-caremanager/<int:patient_id>/", views.DetailPatientforCaremanagerView.as_view()),
    path("create/patient-detail-caremanager/", views.CreatePatientContactDetailForCaremanagerView.as_view()), #create patient for care manager
    path("update/patient-detail-caremanager/<int:patient_id>/",views.UpdatePatientContactDetaiForCaremanagerView.as_view()),
    path("get/patient-detail-caremanager/<int:pk>/", views.PatientDetailProviderAPIView.as_view()),


    # Call Log API's
    path("call-log/start/", views.PatientCallLogStartAPIView.as_view()),
    path("call-log/end/", views.PatientCallLogEndAPIView.as_view()),
    path("call-log/<int:patient_id>/", views.PatientCallLogDetail.as_view()),

    # Patient Summary Report
    path("patient_summary/<int:patient_id>/", views.PatientSummaryView.as_view()),
    
    # Monthly Care Report
    path("monthly-care-report/<int:pk>/", views.PatientMonthlyReportAPIView.as_view()),
    path("get/patient-call-log/list/<int:patient_id>/", views.GetPatientCallLogsListView.as_view()),
    
    path("vital-call-log/create/", views.CreateVitalCallLogView.as_view()),
    path("vital-call-log/get/<int:pk>/", views.GetVitalCallLogView.as_view()),
    path("vital-call-log/update/<int:call_log_id>/<int:patient_id>/", views.UpdateVitalCallLogView.as_view()),

    path("medication-call-log/create/", views.CreateMedicalConditionCallLogView.as_view()),
    path("medication-call-log/get/<int:pk>/", views.GetMedicalConditionCallLogView.as_view()),
    path("medication-call-log/update/<int:call_log_id>/<int:patient_id>/", views.UpdateMedicationCallLogView.as_view()),

    path("assessment-call-log/create/", views.CreateAssessmentCallLogView.as_view()),
    path("assessment-call-log/get/<int:pk>/", views.GetAssessmentCallLogView.as_view()),
    path("assessment-call-log/update/<int:call_log_id>/<int:patient_id>/", views.UpdateAssessmentCallLogView.as_view()),

    path("annual-wellness-visit-call-log/create/", views.CreateAnnualWellnessVisitCallLogView.as_view()),
    path("annual-wellness-visit-call-log/get/<int:pk>/", views.GetAnnualWellnessVisitCallLogView.as_view()),
    path("annual-wellness-visit-call-log/update/<int:call_log_id>/<int:patient_id>/", views.AnnualWellnessVisitCallLogUpdateApi.as_view()),

    path("self-management-plan-call-log/create/", views.CreateSelfManagementPlanCallLogView.as_view()),
    path("self-management-plan-call-log/get/<int:pk>/", views.GetSelfManagementPlanCallLogView.as_view()),

    path('create/patient/outreach/', views.GetPatientOutreachView.as_view()),
    path('get/patient/outreach/deatils/<int:outreach_id>/', views.PatientOutreachDetailsView.as_view()),
    path('outreach/update/<int:outreach_id>/', views.PatientOutreachUpdateView.as_view()),
    path('outreach/update/detail/<int:outreach_id>/', views.UpdateOutreachView.as_view()),

    path("send/patient/summary/mail/<int:patient_id>/",views.SendPatientSummaryMailView.as_view()),
    
    path('get/screening/name/', views.ScreeningNameView.as_view()),
    path('get/patient/calllog/<int:patient_id>/', views.GetPatientCallLogWithTypeView.as_view()),
    
    path('get/caremanager/calllog/patient/count/', views.GetCareManagerCallLogPatientCount.as_view()),
    path('get/default/caremanager/calllog/patient/count/', views.GetDefaultCareManagerCallLogPatientCount.as_view()),
    path('get/caremanager/calllog/patient/detail/', views.CareManagerCallLogPatientDetail.as_view()),
    path('get/caremanager/patient/above/twenty/min/', views.GetCMTwentyMinCallLogPatientCount.as_view()),

    path("annual-wellness-visit/update/<int:call_log_id>/<int:patient_id>/", views.AnnualWellnessVisitCallLogUpdateApi.as_view()),
    path("self-management-plan-call-log/update/<int:call_log_id>/<int:patient_id>/", views.GetSelfManagementPlanCallLogUpdateView.as_view()),
    
    # Default Problem/allergy apis
    path("default/load-all/issues/<int:patient_id>/", views.DefaultLoadAllIssuesView.as_view()),
    path("default/problems/", views.DefaultProblemCreateView.as_view()),
    path("default/problems/<int:problem_id>/", views.DefaultProblemUpdateView.as_view()),
    path("default/problems/update/<int:problem_id>/", views.DefaultProblemRetrieveView.as_view()),
    
    path("default/allergie/", views.DefaultAllergieCreateView.as_view()),
    path("default/allergie/<int:allergie_id>/", views.DefaultAllergieUpdateView.as_view()),
    path("default/allergie/retrieve/<int:allergie_id>/", views.DefaultAllergieRetrieveView.as_view()),
    
    path("default/immunization/", views.DefaultImmunizationCreateView.as_view()),
    path("default/immunization/<int:immunization_id>/", views.DefaultImmunizationUpdateView.as_view()),
    path("default/immunization/retrieve/<int:immunization_id>/", views.DefaultImmunizationRetrieveView.as_view()),
    
    path("default/labreports/", views.DefaultLabReportsCreateView.as_view()),
    path("default/labreports/<int:labreports_id>/", views.DefaultLabReportsUpdateView.as_view()),
    path("default/labreports/retrieve/<int:labreports_id>/", views.DefaultLabReportsRetrieveView.as_view()),

    path("default/procedures/", views.DefaultProceduresCreateView.as_view()),
    path("default/procedures/<int:procedures_id>/", views.DefaultProceduresUpdateView.as_view()),
    path("default/procedures/retrieve/<int:procedures_id>/", views.DefaultProceduresRetrieveView.as_view()),
    
    path("default/patientdocs/", views.DefaultPatientDocsCreateView.as_view()),
    path("default/patientdocs/<int:patientdocs_id>/", views.DefaultPatientDocsUpdateView.as_view()),
    path("default/patientdocs/retrieve/<int:patientdocs_id>/",views.DefaultPatientDocsRetrieveView.as_view()),

    path("create-view-log/", views.ViewLogsCreate.as_view()),
    path("get-view-log/<int:patient_id>/", views.ViewLogsGet.as_view()),
    
    path("audit/log/update/<int:patient_id>/", views.AuditLogUpdateAPI.as_view()),

    path("goal/status/update/<int:goal_id>/", views.UpdateGoalStatus.as_view()),
    
    path('create/patient/session/',views.PatientSessionView.as_view()),

    path("outreach/search/", views.OutreachAPIView.as_view()),

    # AWV API's
    path("annual-wellness-visit/load/who/", views.AnnualWellnessVisitLoadWhoView.as_view()),
    path("annual-wellness-visit/load/how-often/", views.AnnualWellnessVisitLoadHowOftenView.as_view()),
    
    path("get/caregap/screening/<int:screening_id>/", views.ScreeningWhoOftenView.as_view()),

    path("task/status/update/<int:goaltask_id>/", views.UpdateGoalTaskStatus.as_view()),

    # Caremanager Task
       
    path("mannual/time/create/", views.CreateMannualTimeView.as_view()),#create call logs 
    path("total/mannual_time/<int:pk>/", views.TotalMannualTimeView.as_view()), #get manuual time list
    
    path('create/caremanager/task/', views.GetCreateCareManagerTaskView.as_view()), #Task create      
    path('outreach/task/list/', views.GetPatientOutreachTaskView.as_view()), #Outreach List/Coordination Summary (task+outreach) data list and search
    path('task/detail/update/<int:task_id>/', views.TaskDetailUpdateView.as_view()), #Task update and deatil 
    
    path("general_notes-call-log/create/", views.CreateGeneralNotesCallLogView.as_view()),
    path("general_notes-call-log/get/<int:pk>/", views.GetGeneralNotesCallLogView.as_view()),
    path("general_notes-call-log/update/<int:call_log_id>/<int:patient_id>/", views.GeneralNotesCallLogUpdateApi.as_view()),
    path("task_outreach_call_log/list/<int:patient_id>/", views.PatientTaskOutreachCallLogList.as_view()),
    # clinical profile

    path("problems/list/<int:patient_id>/", views.problemsListView.as_view()),
    path("allergies/list/<int:patient_id>/", views.AllergiesListView.as_view()),
    path("immunization/list/<int:patient_id>/", views.ImmunizationListView.as_view()),
    path("labreports/list/<int:patient_id>/", views.LabreportsListView.as_view()),
    path("patientdoc/list/<int:patient_id>/", views.PatientDocListView.as_view()),
    path("procedure/list/<int:patient_id>/", views.ProceduresListView.as_view()),

    path("get/session/time/list/<int:patient_id>/", views.GetSessionTimeList.as_view()),
    path("create/caremanager_notes/", views.CreateCareManagerNotesView.as_view()), #create caremanger notes
    path('care_manager_notes/detail/update/<int:cm_notes_id>/', views.CareManagerNotesDetailUpdateView.as_view()), #caremanger notes update and deatil 
    path("show/patient/duration/stats/", views.ShowPatientDurationStatsView.as_view()), #show count in bar graph
    path("task/history/list/<int:patient_id>/", views.TaskHistoryListView.as_view()), #task history list
    path("outreach/history/list/<int:patient_id>/", views.OutreachHistoryListView.as_view()), #outreach history list
    path("cm_notes/history/list/<int:patient_id>/", views.CareManagerNotesHistoryListView.as_view()), #care manager notes history list
    
    path("get/coordination/report/<int:patient_id>/",views.CoordinationReportView.as_view()),
    path("get/coordination/patient/list/", views.CoordinationPatientList.as_view()),

    path('get/unassign/provider/patient/<int:provider_id>/', views.GetUnAssignProviderPatient.as_view()),
]
