from django.urls import path
from apps.account_manager import views


urlpatterns = [
    path("caremanager/", views.CareManagerApiView.as_view()),
    path("caremanager/retrive/<str:id>/", views.CareManagerRetriveApiView.as_view()),
    path("practice/admin/create/", views.PracticeAdminCreateApiView.as_view()),
    path(
        "practice/admin/retrive/<int:id>/", views.PracticeAdminRetriveApiView.as_view()
    ),
    path("provider/", views.ProviderAPIView.as_view()),
    path("provider/<int:provider_id>/", views.ProviderDetailUpdateView.as_view()),
    path("count/providers/caremanager/patient/", views.CountProviderCareManagerPatientApiView.as_view()),
    path("caremanager/provider/", views.CareManagerProviderApiView.as_view()),
    path("caremanager/provider/detail/<provider_id>/", views.CareManagerProviderDetailApiView.as_view()),
    path("patientlist-for-caremanager/", views.PatientListForCareManagerApiView.as_view()),
    path("caremanager/patient/<int:pk>/", views.RetrieveCaremanagerPatientProfile.as_view()),
    path("caremanager/patient/povider/mapping/multiple-Patient/", views.PatientProviderMappingMultiplePatient.as_view()),

    path("get/caremanager/patient/calllog/", views.CareManagerPatientCallLog.as_view()),

    # Caremanager task listing
    path("caremanager/task/list/", views.CaremanagerTaskListApiView.as_view()),
    path("chronic/patient/list/", views.ChronicPatientCountApiView.as_view()),
    
    # outreach provider list
    path("outreach/providers/list/", views.OutreachProviderGetApi.as_view()),

    # Patient Stats in caremanager dashboard page
    path("patient/stats/total-patient/list/", views.PatientStatsTotalPatientAPIView.as_view()),
    path("patient/stats/enrolled-patient/list/", views.PatientStatsEnrolledPatientAPIView.as_view()),
    path("patient/stats/inactive-patient/list/", views.PatientStatsInactivePatientAPIView.as_view()),
    path("patient/stats/not-reachable-patient/list/", views.PatientStatsNotReachablePatientAPIView.as_view()),

    # Import Patient in bulk
    path("caremanager/bulk-upload/patient/", views.CaremanagerBulkUploadPatient.as_view()),
    path("caremanager/bulk-upload/patient/template/", views.CaremanagerBulkUploadPatientTemplate.as_view()),

    # Import Provider in bulk
    path("caremanager/bulk-upload/provider/", views.CaremanagerBulkUploadProvider.as_view()),
    path("caremanager/bulk-upload/provider/template/", views.CaremanagerBulkUploadProviderTemplate.as_view()),

    path("caremanager/patients/", views.CaremanagerPatientCountAPIView.as_view()),
    path("provider/patients/", views.ProviderPatientCountAPIView.as_view()),
    path("chronic/patients/", views.ChronicConditionPatientCountAPIView.as_view()),
    # Get hoapital of login care manager 
    path("get/cm/hospital/",views.GetCaremanagerHospitalView.as_view()), 
    path("get/hospital/caremanager/", views.GetHospitalCareManagerApiView.as_view()),
    # path("",views.Import_Excel_pandas,name="Import_Excel_pandas"),
   
 path('Import_Excel_pandas/', views.Import_Excel_pandas,name="Import_Excel_pandas"),
    
    path('caremanager/duration/<int:caremanager_id>/<int:year>',views.CareManagerDuration.as_view(),name='caremanager_duration'),
    path('caremanager/completed_mins/<int:care_manager_id>',views.CareManagerCompletedMins.as_view(),name='caremanager_completed_mins'),
    
    path('assign/patient/list/<int:provider_id>/', views.AssignPatientListView.as_view()),
   
    path('export_xlshhet/',views.Export_execl.as_view(),name='export_execl'),
    path('caremanager/list/sort/',views.GetCareManagerListSortByMinutesApiView.as_view()),
    path("caremanager/list/", views.GetCareManagerlistApiView.as_view()),    
   
    

]
