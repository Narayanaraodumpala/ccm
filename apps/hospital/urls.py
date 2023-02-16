from django.urls import path
from apps.hospital import views
from django.conf import settings

from django.conf.urls.static import static

urlpatterns = [
    # Appointment urls
    path("appointment/", views.AppointmentView.as_view(), name="appointment"),
    path("appointment/detail/<int:pk>/", views.AppointmentDetailView.as_view()),
    # Hospital urls
    path("", views.HospitalView.as_view(), name="hospital"),
    path("detail/<int:pk>/", views.HospitalDetailView.as_view()),
    path(
        "branch/", views.HospitalBranchView.as_view(), name="hospital-branch"
    ),
    path("branch/detail/<int:pk>/", views.HospitalBranchDetailView.as_view()),
    # Treatment urls
    path("treatment/", views.TreatmentView.as_view(), name="treatment"),
    path("treatment/detail/<int:pk>/", views.TreatmentDetailView.as_view()),
    # Department urls
    path("department/", views.DepartmentView.as_view(), name="department"),
    path("department/detail/<int:pk>/", views.DepartmentDetailView.as_view()),

    # <--- Chronic Disease urls ---> #
    path("bulk-create/chronic-disease/", views.UploadChronicDiseaseAPIView.as_view()),
    # Will be used by super admin
    path("get/default/chronic-diseases/", views.ChroniConditionAPIView.as_view()),

    # Create Chronic diseases; Asthma, etc object of patient, used by caremanager
    path('patient/chrnonic-disease/', views.PatientChronicDiseaseView.as_view()),

    # List Chronic diseases of patient, used by caremanager
    path('patient/chrnonic-disease/list/<int:patient_id>/', views.PatientChronicDiseaseListView.as_view()),

    # Update a Chronic diseases row of patient, used by caremanager
    path('patient/chrnonic-disease/<int:patient_chronic_id>/<int:patient_id>/', views.PatientChronicDiseaseUpdateView.as_view()),

    # Used in Patient Profile, sidebar to show has_disease
    path('patient/chrnonic-disease/<int:patient_id>/', views.PatientChronicDiseaseRetrieveView.as_view()),

    # Assign list of CD to patient
    path('patient/chrnonic-disease/assign/', views.AssignPatientChronicDiseaseView.as_view()),

    # Used by super admin
    path('chronic-disease/update/<int:chronic_id>/', views.ChronicDiseaseUpdateView.as_view()),

    path('upload-npi-data/', views.UploadNPIDataAPIView.as_view()),
    path("get/hospital/data/list/", views.GetHospitaDataListView.as_view()),
    path('statics/', views.StatisticsView.as_view()),
    path('user/<int:pk>/', views.HospitalRelatedUserView.as_view()),
    path('branch/location/<int:pk>/', views.HospitalBranchLocationView.as_view()),
    path('medication/create/', views.MedicationView.as_view()),
    path('medication/<int:patient_id>/', views.MedicationOfPatienView.as_view()),
    path('medication/update/<int:pk>/<int:patient_id>/', views.MedicationUpdateView.as_view()),

    # Fetch NPI Taxonomy Desciption API
    path('taxonomy/get/', views.TaxonomyDescriptionView.as_view()),
    
    # UnAssign list of CD to patient
    path('patient/chrnonic-disease/unassign/', views.UnAssignPatientChronicDiseaseView.as_view()),
    
    # List Medication Chronic diseases 
    path('medication/chronic-disease/list/', views.PatientMedicationChronicDiseaseListView.as_view()),

    # list medication of patient
    path('medication/list/<int:patient_id>/', views.MedicationListView.as_view()),

    ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
