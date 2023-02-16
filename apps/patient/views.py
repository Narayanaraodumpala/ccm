import datetime

import pandas as pd
from threading import Thread
from itertools import chain
import random
from rest_framework import serializers

from django.db.models import Q
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated

from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import BrowsableAPIRenderer

from django.db.models import Value
from django.db.models.functions import Concat
from apps.hospital.models import Appointment, HospitalBranch
from apps.account_manager.models import (
    Patient,
    Provider,
    PatientContactDetails,
    CareManager,
    PatientSession,
)
from apps.hospital.models import Treatment

from apps.patient.models import (
    AnnualWellnessVisitCallLog,
    AnnualWellnessVist,
    AssessmentCallLog,
    Assistance,
    CareManagerNotes,
    GeneralNotesCallLog,
    Goal,
    GoalChallenges,
    GoalTask,
    PatientOutreach,
    ProgramInformation,
    BMI,
    BloodPressure,
    BloodGlucose,
    PulseOx,
    HBA1C,
    Cholesterol,
    SelfManagementPlanCallLog,
    StepsToAchieveGoal,
    Task,
    Notes,
    PatientCallLog,
    MedicationNotes,
    MedicalConditionCallLog,
    ViewLogs,
    VitalCallLog,
    ScreeningName,
    Problems,
    Allergies,
    Immunization,
    LabReports,
    LabReports,
    Procedures,
    PatientDocs,
    AWVWho,
    AWVHowOften,
    ScreeningWhoOften,
)
from apps.patient.serializers import (
    AddDailyGoalTaskSerializer,
    AnnualWellnessVisitCallLogSerializer,
    AnnualWellnessVisitSerializer,
    AssessmentCallLogSerializer,
    CMTwentyMinCallLogPatientCountSerializer,
    CareManagerDetailUpdateSerializer,
    CareManagerNotesHistoryListSerializer,
    CareManagerNotesSerializer,
    CMTwentyMinCallLogPatientCountSerializer,
    CareManagerDetailUpdateSerializer,
    CareManagerNotesSerializer,
    GoalTaskSerializer,
    ImmunizationUpdateSerializer,
    InterventionSerializer,
    OutreachHistoryListSerializer,
    PatientOutreachSerializer,
    ProgramInformationSerializer,
    CareManagerDashboardDetailSerializer,
    GetappointmentsProviderCountSerializer,
    BMISerializer,
    BloodPressureSerializer,
    BloodGlucoseSerializer,
    PulseOxSerializer,
    HBA1CSerializer,
    CholesterolSerializer,
    NotesSerializer,
    PatientContactDetailsSerializer,
    PatientContactDetailsCreateSerializer,
    GoalSerializer,
    RecurrencBiWeeklyOutreachSerializer,
    RecurrencMonthlyOutreachSerializer,
    RecurrenceDailyOutreachSerializer,
    SelfManagementPlanCallLogSerializer,
    ShowPatientDurationStatsSerializer,
    TaskCreateSerializer,
    MedicationNotesSerializer,
    PatientMonthlyReportSerializer,
    CreatepatientforcaremanagerSerializer,
    PatientCallLogSerializer,
    PatientCallLogEndSerializer,
    PatientVitalGlobalSearchSerializer,
    PatientSummarySerializer,
    ProgramInformationTypeSerializer,
    ProgramInformationTypeDetailSerializer,
    MedicationCallLogSerializer,
    TaskDetailUpdateSerializer,
    TaskHistoryListSerializer,
    UnassignProviderPatientSerializer,
    ViewLogsGetSerializer,
    ViewLogsSerializer,
    VitalCallLogSerializer,
    GetPatientCallLogsListSerializer,
    UpdatePatientOutreachStatusSerializer,
    PatientDetailSerializer,
    GoalCreateSerializer,
    ScreeningNameSerializer,
    PatientCallLogWithTypeSerializer,
    CareManagerPatientCountCallLog,
    AnnualWellnessVisitCreateSerializer,
    ProblemsSerializer,
    DefaultLoadAllIssuesSerializer,
    AllergiesSerializer,
    ImmunizationSerializer,
    LabReportsSerializer,
    ProceduresSerializer,
    PatientDocssSerializer,
    GoalsTaskSerializer,
    UpdateGoalStatusSerializer,
    CareManagerPatientDefaultCountCallLog,
    PatientSessionSerializer,
    PatientOutreachListSerializer,
    CallLogPatientDetailSerializer,
    OutreachSerializer,
    AWVWhoSerializer,
    CreateMannualTimeSerializer,
    AWVHowOftenSerializer,
    UpdateTaskStatusSerializer,
    GetSessionWhoSerializers,
    PatientDocssRetrieveSerializer,
    LabReportsRetrieveSerializer,
    ProblemsRetrieveSerializer,
    AllergiesRetrieveSerializer,
    ImmunizationRetrieveSerializer,
    ProceduresRetrieveSerializer,
    CareManagerTaskSerializer,
    GeneralNotesCallLogSerializer,
    AllergieSerializer, CoordinationReportSerializer, CoordinationPatientSerializer,
    SessionTimeSerializer, AllergiesCreateSerializer, AllergiesUpdateSerializer,
    ImmunizationCreateSerializer, LabReportsCreateSerializer, LabReportsUpdateSerializer,
    ProceduresCreateSerializer, ProceduresUpdateSerializer, PatientDocsCreateSerializer,
    PatientDocsUpdateSerializer, ProblemsCreateSerializer, ProblemsUpdateSerializer, TotalMannualSerializer,
    PatientOutreachUpdateSerializer, RecurrencWeeklyOutreachSerializer,
)
from apps.account_manager.serializers import (
    PatientProviderMappingSerializer,
    PatientSerializer,
    CommunicationSerializers,
    ProviderSerializer,
    ProvidersPatientListSerializer,
    ProviderStatsSerializer,
    PatientProviderMappingCreateSerializer,
    ProviderAssignedPatientSerializer,
)
from apps.patient.models import Intervention, ProgramInformationType
from apps.patient.utils import (
    AnnualWellnessVisitFilter,
    PatientTaskFilter,
    get_last_updated_object,
    create_scheduled_outreach_object,
    CustomPageNumberPagination,
    taskoutreachsearch,
    taskoutreachcalllog_combine,
    FilterData,
    FilterSession,
)
from apps.account_manager.utils import SendMail, PatientOutreachFilter, TaskFilter, UnAssignProviderPatientSearch, build_task_data
from apps.account_manager import create_response_util
from apps.account_manager.utils import (
    create_related_user,
    create_patient_user_for_care_manager,
    PatientFilter,
)
from apps.patient.serializers import (
    PatientKeyStatSerializer,
    PatientTreatmentSerializer,
    GetPatientMedicationsSerializer,
    ShowPatientStatsSerializer,
    CareManagerDashboardDetailSerializer,
    AssistanceSerializer,
    StepsToAchieveGoalSerializer,
    GoalChallengesSerializer,
    TotalMannualSerializer, ImmunizationUpdateSerializer,
)
from apps.account_manager.models import Communication, PatientProviderMapping, User
from apps.account_manager.create_response_util import ApiRenderer


class PatientView(APIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination()

    """
    List all patients, or create a new patients.
    """

    def get(self, request):
        try:
            patients = Patient.objects.get_queryset().order_by("id")
            patient = self.pagination_class.paginate_queryset(patients, request)
            serializer = self.serializer_class(patient, many=True)
            pages = self.pagination_class.get_paginated_response(serializer.data)

            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=pages.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def post(self, request):
        try:
            serializer = PatientSerializer(data=request.data)
            if serializer.is_valid():
                user = create_related_user(request.data, "PATIENT")
                serializer.save(user=user)
                # thread = Thread(target=SendMail.user_send_email, args=(data,))
                # thread.start()
                SendMail.user_send_credential_email(
                    user, password=request.data["password"]
                )
                SendMail.user_send_welcome_email(user)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PatientDetailView(APIView):
    """
    Retrieve, update or delete a patients instance.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            data = Patient.objects.get(pk=pk)
            return data
        except Patient.DoesNotExist:
            return None

    def get(self, request, pk):
        try:
            patient = self.get_object(pk)
            if patient is not None:
                serializer = PatientSerializer(patient)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def put(self, request, pk):
        try:
            patient = self.get_object(pk)
            if patient is not None:
                serializer = PatientSerializer(patient, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.data,
                        errors=None,
                    )
                else:
                    return create_response_util.create_response_data(
                        message="failed",
                        status=status.HTTP_400_BAD_REQUEST,
                        data=None,
                        errors=serializer.errors,
                    )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def delete(self, request, pk):
        try:
            patient = self.get_object(pk)
            if patient is not None:
                patient.delete()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=None,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CommunicationCreateApiView(APIView):
    serializer_class = CommunicationSerializers
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            communication = Communication.objects.all()
            if communication:
                serializer = self.serializer_class(communication, many=True)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CommunicationRetriveApiView(APIView):
    serializer_class = CommunicationSerializers
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            object = Communication.objects.filter(id=id)
            if object:
                serializer = self.serializer_class(object, many=True)

                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def put(self, request, id):
        try:
            issue = Communication.objects.get(id=id)
            serializer = self.serializer_class(issue, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def delete(self, request, id):
        try:
            object = Communication.objects.get(id=id)
            if object:
                object.is_active = False
                object.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=None,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PatientProviderMappingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            patient_provider = PatientProviderMapping.objects.all()
            patient_provider_serializer = PatientProviderMappingSerializer(
                patient_provider, many=True
            )
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=patient_provider_serializer,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def post(self, request):
        try:
            serializer = PatientProviderMappingCreateSerializer(data=request.data)

            # Validate pri & sec provider
            if request.data.get("primary_provider") and request.data.get(
                    "secondary_provider"
            ):
                if request.data.get("primary_provider") == request.data.get(
                        "secondary_provider"
                ):
                    message = "Primary provider & secondary provider can not be same"
                    return create_response_util.create_response_data(
                        message=message,
                        status=status.HTTP_400_BAD_REQUEST,
                        data=None,
                        errors=None,
                    )
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class UploadPatientDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            file = request.FILES["file"]
            df = pd.read_excel(file, engine="openpyxl")
            for i in df.values:
                is_patient = Patient.objects.filter(name=i[0], birth_date=i[1])
                if not is_patient:
                    obj = Patient.objects.create(name=i[0], birth_date=i[1])
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=None,
                errors=None,
            )
        except Exception as e:
            return Response(
                data={
                    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": str(e),
                }
            )


class ProgramInformationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        try:
            program_information = ProgramInformation.objects.filter(
                patient_id=patient_id
            ).order_by("-created_at")
            serializer = ProgramInformationTypeDetailSerializer(
                program_information, many=True
            )

            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class ProgramInformationUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, patient_id, program_info_id):
        try:
            program_information = ProgramInformation.objects.filter(
                patient_id=patient_id, id=program_info_id
            ).last()
            serializer = ProgramInformationSerializer(
                program_information, data=request.data
            )
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class ProgramInformationCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = ProgramInformationSerializer(data=request.data)
            if serializer.is_valid():
                obj = serializer.save()
                obj.created_by = request.user.get_full_name()
                obj.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GoalTaskView(APIView):
    """
    create and get all GoalTask for patient
    """

    permission_classes = [IsAuthenticated]
    serializer = InterventionSerializer
    queryset = Intervention.objects.all()

    def get(self, request):
        try:
            data = Intervention.objects.all()
            if data:
                serializer = self.serializer(data, many=True)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def post(self, request):
        try:
            # cm = CareManager.objects.filter(user=request.user).last()
            serializer = InterventionSerializer(data=request.data)
            if serializer.is_valid():
                obj = serializer.save()
                obj.created_by = request.user.get_full_name()
                obj.save()
                # serializer.save()
                # interven = Intervention.objects.get(id=serializer.data["id"])
                # Task.objects.create(intervention=interven, patient=interven.patient, care_manager=cm,
                #                     task_date=interven.date)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_400_BAD_REQUEST,
                data=None,
                errors=serializer.errors,
            )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    # def post(self, request):
    #     try:
    #         caremager_id = request.user.id
    #         care_manager = CareManager.objects.get(user__id=caremager_id)
    #         if request.data['recurrence_pattern']:
    #             if request.data.get('daily'):
    #                 serializer = AddDailyGoalTaskSerializer(data=request.data)
    #             # elif request.data.get('weekly'):
    #             #     serializer = RecurrencWeeklyOutreachSerializer(data=request.data)
    #             if serializer.is_valid():
    #                 obj = serializer.save(care_manager=care_manager)
    #                 obj.time_spent = datetime.timedelta(minutes=int(request.data['time_spent']))
    #                 obj.save()
    #                 return create_response_util.create_response_data(
    #                     message="success",
    #                     status=status.HTTP_200_OK,
    #                     data=None,
    #                     errors=None,
    #                 )
    #             else:
    #                 return create_response_util.create_response_data(
    #                     message="failed",
    #                     status=status.HTTP_400_BAD_REQUEST,
    #                     data=serializer.errors,
    #                     errors=None,
    #                 )
    #         else:
    #             serializer = self.serializer_class(data=request.data)
    #             if serializer.is_valid():
    #                 obj = serializer.save(care_manager=care_manager)
    #                 obj.time_spent = datetime.timedelta(minutes=int(request.data['time_spent']))
    #                 obj.save()
    #                 return create_response_util.create_response_data(
    #                     message="success",
    #                     status=status.HTTP_200_OK,
    #                     data=serializer.data,
    #                     errors=None,
    #                 )
    #             else:
    #                 return create_response_util.create_response_data(
    #                     message="failed",
    #                     status=status.HTTP_400_BAD_REQUEST,
    #                     data=serializer.errors,
    #                     errors=None,
    #                 )
    #     except Exception as e:
    #         return create_response_util.create_response_data(
    #             message="failed",
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             data=None,
    #             errors=str(e),
    #         )


class GoalTaskDetailsView(APIView):
    """
    get, update and delete GoalTask details for patient
    """

    serializer =  InterventionSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            data = Intervention.objects.filter(id=id)
            if data:
                serializer = self.serializer(data, many=True)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def put(self, request, id):
        try:
            data = Intervention.objects.filter(id=id).first()
            if data:
                serializer = self.serializer(data, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.data,
                        errors=None,
                    )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def delete(self, request, id):
        try:
            if id:
                profile = Intervention.objects.get(id=id)
                profile.delete()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=None,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


# Annual wellness visit


class AnnualWellnessVisitView(generics.ListCreateAPIView):
    """
    create and get all Annual Wellness Visit List
    """

    permission_classes = [IsAuthenticated]
    serializer_class = AnnualWellnessVisitSerializer
    queryset = AnnualWellnessVist.objects.all().order_by("-created_at")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AnnualWellnessVisitFilter

    def get_queryset(self, *args, **kwargs):
        patient = Patient.objects.filter(id=self.kwargs["patient_id"]).last()
        queryset = AnnualWellnessVist.objects.filter(patient=patient).order_by(
            "-created_at"
        )
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, patient_id):
        try:
            queryset = self.filter_queryset(self.get_queryset(patient_id=patient_id))
            serializer = self.serializer_class(queryset, many=True)
            # return Response(serializer.data)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def post(self, request):
        try:
            serializer = AnnualWellnessVisitCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_400_BAD_REQUEST,
                data=None,
                errors=serializer.errors,
            )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class AnnualWellnessVisitDetailsView(generics.ListCreateAPIView):
    serializer_class = AnnualWellnessVisitSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AnnualWellnessVisitFilter

    def get_queryset(self, *args, **kwargs):
        patient_id = self.kwargs.get("patient_id")
        if patient_id:
            queryset = AnnualWellnessVist.objects.filter(patient=patient_id).order_by(
                "-modified_at"
            )
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, patient_id):
        try:
            annual_wellness = self.filter_queryset(self.get_queryset())
            serializer = self.serializer_class(annual_wellness, many=True)
            # return Response(serializer.data)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class AnnualWellnessVisitUpdateView(generics.ListCreateAPIView):
    serializer_class = AnnualWellnessVisitCreateSerializer

    # permission_classes = [IsAuthenticated]

    def patch(self, request, patient_id):
        try:
            data = request.data
            errors = []
            updated_data = []
            for obj in data:
                annual_wellness = AnnualWellnessVist.objects.filter(
                    id=obj.get("id"), patient=patient_id
                ).last()
                serializer = self.serializer_class(
                    annual_wellness, data=obj, partial=True
                )
                if serializer.is_valid():
                    serializer.save()
                    updated_data.append(serializer.data)

                else:
                    errors.append(serializer.errors)

            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=updated_data,
                errors=errors,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class ShowPatientStatsView(APIView):
    serializer = ShowPatientStatsSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cm = CareManager.objects.filter(user=request.user).last()
            serializer = self.serializer(cm)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CareManagerDashboardDetailView(APIView):
    serializer = CareManagerDashboardDetailSerializer

    def get(self, request):
        try:
            cm = CareManager.objects.filter(user=request.user).last()
            serializer = self.serializer(cm)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PatientKeyStatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            data = Patient.objects.get(pk=pk)
            return data
        except Patient.DoesNotExist:
            return None

    def get(self, request, pk):
        try:
            patient = self.get_object(pk)
            serializer = PatientKeyStatSerializer(patient)
            if patient is not None:
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PatientTreatmentCommunicationView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            data = Patient.objects.get(pk=pk)
            return data
        except Patient.DoesNotExist:
            return None

    def get(self, request, pk):
        try:
            patient = self.get_object(pk)
            serializer = PatientTreatmentSerializer(patient)
            if patient is not None:
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class TotalMannualTimeView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            data = Patient.objects.get(pk=pk)
            return data
        except Patient.DoesNotExist:
            return None

    def get(self, request, pk):
        try:
            patient = self.get_object(pk)
            serializer = TotalMannualSerializer(patient)
            if patient is not None:
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class ProviderPatientListView(APIView):
    serializer = ProvidersPatientListSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            obj = Provider.objects.filter(id=id).last()
            ppms = PatientProviderMapping.objects.filter(primary_provider=obj)
            ppm_pt_list = []
            for ppm in ppms:
                ppm_pt_list.append(ppm.patient.pk)
            patient_objs = Patient.objects.filter(id__in=ppm_pt_list)
            serializer = self.serializer(patient_objs, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class ProviderAssignedPatientView(APIView):
    # serializer = ProviderAssignedPatientSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            data = Provider.objects.get(pk=pk)
            return data
        except Provider.DoesNotExist:
            return None

    def get(self, request, pk):
        try:
            provider_id = self.get_object(pk)
            serializer = ProviderAssignedPatientSerializer(provider_id)
            if provider_id is not None:
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class ProviderStatsView(APIView):
    # serializer = ProviderStatsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            data = Provider.objects.get(pk=pk)
            return data
        except Provider.DoesNotExist:
            return None

    def get(self, request, pk):
        try:
            provider_id = self.get_object(pk)
            serializer = ProviderStatsSerializer(provider_id)
            if provider_id is not None:
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetappointmentsProviderCountView(APIView):
    serializer_class = GetappointmentsProviderCountSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            data = Appointment.objects.filter(pk=pk)
            serializer = self.serializer_class(
                data, context={"request": request, "pk": pk}
            )
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetPatientMedicationsView(APIView):
    serializer_class = GetPatientMedicationsSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            patient_medications = Patient.objects.filter(pk=pk)
            serializer = self.serializer_class(patient_medications)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class BMICreateView(APIView):
    serializer_class = BMISerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class BloodPressureCreateView(APIView):
    serializer_class = BloodPressureSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class BloodGlucoseCreateView(APIView):
    serializer_class = BloodGlucoseSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PulseOxCreateView(APIView):
    serializer_class = PulseOxSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class HBA1CCreateView(APIView):
    serializer_class = HBA1CSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CholesterolCreateView(APIView):
    serializer_class = CholesterolSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class NotesCreateView(APIView):
    serializer_class = NotesSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class BMIListView(APIView):
    serializer_class = BMISerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            obj = Patient.objects.get(pk=patient_id)
            return obj
        except Patient.DoesNotExist:
            return None

    def get(self, request, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                bmis = BMI.objects.filter(patient=patient, is_active=True).order_by(
                    "-created_at"
                )[:5]
                serializer = self.serializer_class(bmis, many=True)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class BMIUpdateView(APIView):
    serializer_class = BMISerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            obj = Patient.objects.get(pk=patient_id)
            return obj
        except Patient.DoesNotExist:
            return None

    def put(self, request, pk, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                bmis = BMI.objects.filter(id=pk, patient=patient).last()
                if not bmis:
                    raise serializers.ValidationError("Bmi object does not exist.")
                serializer = self.serializer_class(bmis, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.data,
                        errors=None,
                    )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class AllBMIListView(generics.ListAPIView):
    serializer_class = BMISerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    search_fields = ("date", "bmi_score", "session_id", "source_entry",)

    def get_queryset(self, *args, **kwargs):
        patient = Patient.objects.filter(id=self.kwargs["patient_id"]).last()
        queryset = BMI.objects.filter(patient=patient, is_active=True).order_by(
            "-created_at"
        )
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, patient_id):
        try:
            bmis = self.filter_queryset(self.get_queryset(patient_id=patient_id))
            serializer = self.serializer_class(bmis, many=True)
            # return Response(serializer.data)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class BloodPressureListView(APIView):
    serializer_class = BloodPressureSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            obj = Patient.objects.get(pk=patient_id)
            return obj
        except Patient.DoesNotExist:
            return None

    def get(self, request, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                bps = BloodPressure.objects.filter(
                    patient=patient, is_active=True
                ).order_by("-created_at")[:5]
                serializer = self.serializer_class(bps, many=True)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class BloodGlucoseListView(APIView):
    serializer_class = BloodGlucoseSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            obj = Patient.objects.get(pk=patient_id)
            return obj
        except Patient.DoesNotExist:
            return None

    def get(self, request, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                bgs = BloodGlucose.objects.filter(
                    patient=patient, is_active=True
                ).order_by("-created_at")[:5]
                serializer = self.serializer_class(bgs, many=True)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class AllBloodGlucoseListView(generics.ListAPIView):
    serializer_class = BloodGlucoseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    search_fields = (
        "date",
        "blood_sugar",
        "notes",
        "session_id",
        "source_entry",
    )

    def get_queryset(self, *args, **kwargs):
        patient = Patient.objects.filter(id=self.kwargs["patient_id"]).last()
        queryset = BloodGlucose.objects.filter(
            patient=patient, is_active=True
        ).order_by("-created_at")
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, patient_id):
        try:
            bmis = self.filter_queryset(self.get_queryset(patient_id=patient_id))
            serializer = self.serializer_class(bmis, many=True)
            # return Response(serializer.data)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class AllBloodPressureListView(generics.ListAPIView):
    serializer_class = BloodPressureSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    search_fields = (
        "date",
        "pulse",
        "notes",
        "session_id",
        "source_entry",
    )

    def get_queryset(self, *args, **kwargs):
        patient = Patient.objects.filter(id=self.kwargs["patient_id"]).last()
        queryset = BloodPressure.objects.filter(
            patient=patient, is_active=True
        ).order_by("-created_at")
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, patient_id):
        try:
            bmis = self.filter_queryset(self.get_queryset(patient_id=patient_id))
            serializer = self.serializer_class(bmis, many=True)
            # return Response(serializer.data)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class BloodGlucoseUpdateView(APIView):
    serializer_class = BloodGlucoseSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            obj = Patient.objects.get(pk=patient_id)
            return obj
        except Patient.DoesNotExist:
            return None

    def put(self, request, pk, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                bgs = BloodGlucose.objects.filter(id=pk, patient=patient).last()
                serializer = self.serializer_class(bgs, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.data,
                        errors=None,
                    )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class BloodPressureUpdateView(APIView):
    serializer_class = BloodPressureSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            obj = Patient.objects.get(pk=patient_id)
            return obj
        except Patient.DoesNotExist:
            return None

    def put(self, request, pk, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                bps = BloodPressure.objects.filter(id=pk, patient=patient).last()
                serializer = self.serializer_class(bps, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.data,
                        errors=None,
                    )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


# class AllBloodPressureListView(generics.ListAPIView):
#     serializer_class = BloodPressureSerializer
#     permission_classes = [IsAuthenticated]
#     filter_backends = (
#         SearchFilter,
#         DjangoFilterBackend,
#     )
#     search_fields = (
#         "date",
#         "pulse",
#         "notes",
#         "session_id","source_entry",
#     )

#     def get_queryset(self, *args, **kwargs):
#         patient = Patient.objects.filter(id=self.kwargs["patient_id"]).last()
#         queryset = BloodPressure.objects.filter(
#             patient=patient, is_active=True
#         ).order_by("-created_at")
#         return queryset

#     def filter_queryset(self, queryset):
#         for backend in list(self.filter_backends):
#             queryset = backend().filter_queryset(self.request, queryset, self)
#         return queryset

#     def list(self, request, patient_id):
#         try:
#             bmis = self.filter_queryset(self.get_queryset(patient_id=patient_id))
#             serializer = self.serializer_class(bmis, many=True)
#             # return Response(serializer.data)
#             return create_response_util.create_response_data(
#                 message="success",
#                 status=status.HTTP_200_OK,
#                 data=serializer.data,
#                 errors=None,
#             )
#         except Exception as e:
#             return create_response_util.create_response_data(
#                 message="failed",
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 data=None,
#                 errors=str(e),
#             )


class GoalView(APIView):
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name"]

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get(self, request):
        try:
            data = Goal.objects.all()
            filter_data = self.filter_queryset(data)
            serializer = self.serializer_class(filter_data, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def post(self, request):
        try:
            serializer = GoalCreateSerializer(data=request.data)
            cm = CareManager.objects.filter(user=request.user).last()
            if serializer.is_valid():
                obj = serializer.save()
                goal = Goal.objects.get(id=obj.pk)
                Task.objects.create(
                    goal=goal,
                    patient=goal.patient,
                    care_manager=cm,
                    task_date=goal.goal_date,
                )
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=None,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )
        except Exception as e:
            print(e)
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PulseOxListView(APIView):
    serializer_class = PulseOxSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            obj = Patient.objects.get(pk=patient_id)
            return obj
        except Patient.DoesNotExist:
            return None

    def get(self, request, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                puls_objs = PulseOx.objects.filter(
                    patient=patient, is_active=True
                ).order_by("-created_at")[:5]
                serializer = self.serializer_class(puls_objs, many=True)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PulseOxUpdateView(APIView):
    serializer_class = PulseOxSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            obj = Patient.objects.get(pk=patient_id)
            return obj
        except Patient.DoesNotExist:
            return None

    def put(self, request, pk, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                puls_objs = PulseOx.objects.filter(id=pk, patient=patient).last()
                serializer = self.serializer_class(puls_objs, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.data,
                        errors=None,
                    )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class HBA1CListView(APIView):
    serializer_class = HBA1CSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            obj = Patient.objects.get(pk=patient_id)
            return obj
        except Patient.DoesNotExist:
            return None

    def get(self, request, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                hbs = HBA1C.objects.filter(patient=patient, is_active=True).order_by(
                    "-created_at"
                )[:5]
                serializer = self.serializer_class(hbs, many=True)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class AllHBA1CListView(generics.ListAPIView):
    serializer_class = HBA1CSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    search_fields = (
        "date",
        "hbaic",
        "notes",
        "session_id",
        "source_entry",
    )

    def get_queryset(self, *args, **kwargs):
        patient = Patient.objects.filter(id=self.kwargs["patient_id"]).last()
        queryset = HBA1C.objects.filter(patient=patient, is_active=True).order_by(
            "-created_at"
        )
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, patient_id):
        try:
            bmis = self.filter_queryset(self.get_queryset(patient_id=patient_id))
            serializer = self.serializer_class(bmis, many=True)
            # return Response(serializer.data)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class AllPulseOxListView(generics.ListAPIView):
    serializer_class = PulseOxSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    search_fields = (
        "date",
        "spo2_value",
        "pulse_rate",
        "notes",
        "session_id",
        "source_entry",
    )

    def get_queryset(self, *args, **kwargs):
        patient = Patient.objects.filter(id=self.kwargs["patient_id"]).last()
        queryset = PulseOx.objects.filter(patient=patient, is_active=True).order_by(
            "-created_at"
        )
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, patient_id):
        try:
            bmis = self.filter_queryset(self.get_queryset(patient_id=patient_id))
            serializer = self.serializer_class(bmis, many=True)
            # return Response(serializer.data)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class HBA1CUpdateView(APIView):
    serializer_class = HBA1CSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            obj = Patient.objects.get(pk=patient_id)
            return obj
        except Patient.DoesNotExist:
            return None

    def put(self, request, pk, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                hbs = HBA1C.objects.filter(id=pk, patient=patient).last()
                serializer = self.serializer_class(hbs, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.data,
                        errors=None,
                    )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CholesterolListView(APIView):
    serializer_class = CholesterolSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            obj = Patient.objects.get(pk=patient_id)
            return obj
        except Patient.DoesNotExist:
            return None

    def get(self, request, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                cholesterol = Cholesterol.objects.filter(
                    patient=patient, is_active=True
                ).order_by("-created_at")[:5]
                serializer = self.serializer_class(cholesterol, many=True)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class AllCholesterolListView(generics.ListAPIView):
    serializer_class = CholesterolSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    search_fields = (
        "date",
        "total_cholesterol",
        "notes",
        "session_id",
        "source_entry",
    )

    def get_queryset(self, *args, **kwargs):
        patient = Patient.objects.filter(id=self.kwargs["patient_id"]).last()
        queryset = Cholesterol.objects.filter(patient=patient, is_active=True).order_by(
            "-created_at"
        )
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, patient_id):
        try:
            bmis = self.filter_queryset(self.get_queryset(patient_id=patient_id))
            serializer = self.serializer_class(bmis, many=True)
            # return Response(serializer.data)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CholesterolUpdateView(APIView):
    serializer_class = CholesterolSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            obj = Patient.objects.get(pk=patient_id)
            return obj
        except Patient.DoesNotExist:
            return None

    def put(self, request, pk, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                cholesterol = Cholesterol.objects.filter(id=pk, patient=patient).last()
                serializer = self.serializer_class(cholesterol, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.data,
                        errors=None,
                    )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class NotesListView(APIView):
    serializer_class = NotesSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            obj = Patient.objects.get(pk=patient_id)
            return obj
        except Patient.DoesNotExist:
            return None

    def get(self, request, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                notes_objs = Notes.objects.filter(patient=patient, is_active=True)
                serializer = self.serializer_class(notes_objs, many=True)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetPatientGoalView(APIView):
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            patient = Patient.objects.filter(pk=pk).last()
            goal = Goal.objects.filter(patient=patient)
            serializer = self.serializer_class(goal, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetPatientGoalDetailView(APIView):
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id, goal_id):
        try:
            patient = Patient.objects.filter(pk=patient_id).last()
            goal = Goal.objects.filter(pk=goal_id, patient=patient)
            serializer = self.serializer_class(goal, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PatientContactDetailCreateView(APIView):
    serializer_class = PatientContactDetailsCreateSerializer
    permission_classes = [IsAuthenticated]


class PatientContactDetailListView(APIView):
    serializer_class = PatientContactDetailsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            obj = Patient.objects.get(pk=patient_id)
            return obj
        except Patient.DoesNotExist:
            return None

    def get(self, request, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                pcd = PatientContactDetails.objects.filter(patient=patient).last()
                serializer = self.serializer_class(pcd)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def put(self, request, patient_id):
        try:
            pcd = PatientContactDetails.objects.filter(patient=patient_id).last()
            serializer = PatientContactDetailsCreateSerializer(pcd, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetPatientTaskView(generics.ListAPIView):
    serializer_class = GoalsTaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)

    # filterset_class = PatientTaskFilter
    def get_queryset(self, *args, **kwargs):
        patient_id = self.kwargs.get("pk", None)
        patient = Patient.objects.filter(pk=patient_id).last()
        goals = Goal.objects.filter(patient=patient)
        return goals

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, pk):
        try:
            goals = self.filter_queryset(self.get_queryset(pk))

            # patient = Patient.objects.filter(pk=pk).last()
            # task = Task.objects.filter(patient=patient)
            serializer = self.serializer_class(goals, many=True)
            # return Response(serializer.data)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CreatePatientTaskView(APIView):
    serializer_class = TaskCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cm = CareManager.objects.filter(user=request.user).last()
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save(care_manager=cm)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class MedicationNotesView(APIView):
    serializer_class = MedicationNotesSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cm = CareManager.objects.filter(user=request.user).last()
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save(care_manager=cm)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class MedicationNotesDetailView(APIView):
    serializer_class = MedicationNotesSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        try:
            mdn = MedicationNotes.objects.filter(patient_id=patient_id)
            serializer = self.serializer_class(mdn, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def put(self, request, patient_id):
        try:
            mdn = MedicationNotes.objects.filter(patient_id=patient_id).last()
            serializer = self.serializer_class(mdn, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CreatePatientforCaremanagerView(APIView):
    serializer_class = CreatepatientforcaremanagerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination()

    """
    List all patients, or create a new patients.
    """

    def get_queryset(self, request):
        queryParams = self.request.GET.get("first_name")  # get queryparameter from url
        if queryParams is None:
            queryset = Patient.objects.all()
        else:
            queryset = Patient.objects.filter(user__first_name=queryParams)
        return queryset

    def get(self, request):
        try:
            patient = self.get_queryset(request)
            patient = self.pagination_class.paginate_queryset(patient, request)
            serializer = self.serializer_class(patient, many=True)
            pages = self.pagination_class.get_paginated_response(serializer.data)

            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=pages.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def post(self, request):
        try:

            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                cm = CareManager.objects.filter(user=request.user).last()
                user, password = create_patient_user_for_care_manager(
                    request.data, "PATIENT"
                )
                serializer.save(user=user, hospital=cm.hospital)
                SendMail.send_email_patient_from_caremanager(user, password)

                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class DetailPatientforCaremanagerView(APIView):
    serializer_class = CreatepatientforcaremanagerSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        try:
            patient = Patient.objects.filter(pk=patient_id).last()
            serializer = self.serializer_class(patient)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def put(self, request, patient_id):
        try:
            patient = Patient.objects.filter(pk=patient_id).last()
            serializer = self.serializer_class(patient, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PatientCallLogStartAPIView(APIView):
    serializer_class = PatientCallLogSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # We get the user id of care manager from FE
            cm_user_id = request.data.get("care_manager", None)
            care_mgr = CareManager.objects.filter(user__id=cm_user_id).last()
            # pop care manager
            request.data.pop("care_manager")
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    care_manager=care_mgr, call_start_datetime=timezone.now()
                )
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PatientCallLogEndAPIView(APIView):
    serializer_class = PatientCallLogEndSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            call_meet_link = request.data.get("call_meet_link", None)
            pcl = PatientCallLog.objects.filter(call_meet_link=call_meet_link).last()

            cm_user_id = request.data.get("care_manager", None)
            care_mgr = CareManager.objects.filter(user__id=cm_user_id).last()
            # pop care manager
            request.data.pop("care_manager")

            # Recorded file
            recording = request.FILES.get("recording", None)
            serializer = self.serializer_class(pcl, data=request.data)
            if serializer.is_valid():
                # Calculate duration
                call_start_datetime = pcl.call_start_datetime
                duration = timezone.now() - call_start_datetime

                serializer.save(
                    care_manager=care_mgr,
                    call_end_datetime=timezone.now(),
                    call_duration=duration,
                    call_status="COMPLETED",
                    recording=recording,
                )
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            print(e)
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PatientCallLogDetail(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PatientCallLogSerializer
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    filterset_class = PatientFilter

    def get_queryset(self, *args, **kwargs):
        cm = CareManager.objects.filter(user=self.request.user.id).last()
        hospital_care_manager = cm.hospital
        patient = Patient.objects.filter(id=self.kwargs["patient_id"]).last()
        queryset = PatientCallLog.objects.filter(
            patient=patient, patient__hospital=hospital_care_manager
        ).exclude(patient__patient_status="SUSPENDED")
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, patient_id):
        try:
            patient = self.filter_queryset(self.get_queryset(patient_id=patient_id))
            data = self.paginate_queryset(patient)
            serializer = self.serializer_class(data, many=True)
            pages = self.get_paginated_response(serializer.data)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PatientVitalGlobalSearch(APIView):
    serializer_class = PatientVitalGlobalSearchSerializer

    def get_object(self, patient_id):
        try:
            patient = Patient.objects.get(pk=patient_id)
            return patient
        except Patient.DoesNotExist:
            return None

    def get(self, request, patient_id):
        try:
            patient = self.get_object(patient_id)
            from_date = self.request.query_params.get("from_date")
            to_date = self.request.query_params.get("to_date")
            serializer = self.serializer_class(
                patient, context={"from_date": from_date, "to_date": to_date}
            )
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PatientSummaryView(APIView):
    serializer_class = PatientSummarySerializer

    def get(self, request, patient_id):
        try:
            patient = Patient.objects.filter(pk=patient_id).last()
            serializer = self.serializer_class(patient, context={"request": request})
            return create_response_util.create_response_data(
                message="successss",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CoordinationReportView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CoordinationReportSerializer

    def get(self, request, patient_id):
        try:
            cm = CareManager.objects.filter(user=request.user, care_manager_status="ACTIVE").first()
            patient = Patient.objects.filter(pk=patient_id, hospital=cm.hospital, caremanager_obj=cm).last()
            serializer = self.serializer_class(patient, context={"request": request})
            return create_response_util.create_response_data(
                message="successss",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CoordinationPatientList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CoordinationPatientSerializer

    def get_queryset(self, *args, **kwargs):
        search = self.request.query_params.get('search')
        cm = CareManager.objects.filter(user=self.request.user).last()
        if search:
            queryset = Patient.objects.annotate(
                full_name=Concat('user__first_name', Value(' '), 'user__last_name')
            ).filter(Q(full_name__icontains=search),
                     hospital=cm.hospital, caremanager_obj=cm)
        else:
            queryset = Patient.objects.filter(caremanager_obj=cm, hospital=cm.hospital)
        return queryset

    def list(self, request):
        try:
            data = self.filter_queryset(self.get_queryset(request)).order_by('-created_at')
            serializer = self.serializer_class(data, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class StepsToAchieveGoalView(APIView):
    serializer_class = StepsToAchieveGoalSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = StepsToAchieveGoal.objects.all()
            serializer = self.serializer_class(data, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GoalChallengesView(APIView):
    serializer_class = GoalChallengesSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = GoalChallenges.objects.all()
            serializer = self.serializer_class(data, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class AssistantView(APIView):
    serializer_class = AssistanceSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = Assistance.objects.all()
            serializer = self.serializer_class(data, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PatientMonthlyReportAPIView(APIView):
    def get_object(self, pk):
        try:
            data = Patient.objects.get(pk=pk)
            return data
        except Patient.DoesNotExist:
            return None

    def get(self, request, pk):
        try:
            patient = self.get_object(pk)
            serializer = PatientMonthlyReportSerializer(
                patient, context={"request": request}
            )
            if patient is not None:
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class ProgramInformationTypeView(APIView):
    serializer_class = ProgramInformationTypeSerializer

    def get(self, request):
        try:
            program_information_type = ProgramInformationType.objects.all()
            serializer = self.serializer_class(program_information_type, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetVitalCallLogView(APIView):
    serializer_class = VitalCallLogSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            patient = Patient.objects.filter(pk=pk).last()
            obj = VitalCallLog.objects.filter(patient=patient)
            serializer = self.serializer_class(obj, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CreateVitalCallLogView(APIView):
    serializer_class = VitalCallLogSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cm = CareManager.objects.filter(user=request.user).last()
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                obj = serializer.save(care_manager=cm)
                obj.call_duration = datetime.timedelta(minutes=int(request.data['call_duration']))
                obj.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class UpdateVitalCallLogView(APIView):
    serializer_class = VitalCallLogSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            obj = Patient.objects.get(pk=patient_id)
            return obj
        except Patient.DoesNotExist:
            return None

    def put(self, request, call_log_id, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                call_log = VitalCallLog.objects.filter(
                    id=call_log_id, patient=patient
                ).last()
                serializer = self.serializer_class(call_log, data=request.data)
                if serializer.is_valid():
                    obj = serializer.save()
                    obj.call_duration = datetime.timedelta(minutes=int(request.data['call_duration']))
                    obj.save()
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.data,
                        errors=None,
                    )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetMedicalConditionCallLogView(APIView):
    serializer_class = MedicationCallLogSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            patient = Patient.objects.filter(pk=pk).last()
            obj = MedicalConditionCallLog.objects.filter(patient=patient)
            serializer = self.serializer_class(obj, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CreateMedicalConditionCallLogView(APIView):
    serializer_class = MedicationCallLogSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cm = CareManager.objects.filter(user=request.user).last()
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                obj = serializer.save(care_manager=cm)
                obj.call_duration = datetime.timedelta(minutes=int(request.data['call_duration']))
                obj.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class UpdateMedicationCallLogView(APIView):
    serializer_class = MedicationCallLogSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            obj = Patient.objects.get(pk=patient_id)
            return obj
        except Patient.DoesNotExist:
            return None

    def put(self, request, call_log_id, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                call_log = MedicalConditionCallLog.objects.filter(
                    id=call_log_id, patient=patient
                ).last()
                serializer = self.serializer_class(call_log, data=request.data)
                if serializer.is_valid():
                    obj = serializer.save()
                    obj.call_duration = datetime.timedelta(minutes=int(request.data['call_duration']))
                    obj.save()
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.data,
                        errors=None,
                    )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetPatientCallLogsListView(APIView):
    serializer_class = GetPatientCallLogsListSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        try:
            patient = Patient.objects.filter(id=patient_id).last()
            serializer = self.serializer_class(
                patient, context={"request": request, "id": patient_id}
            )
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetAssessmentCallLogView(APIView):
    serializer_class = AssessmentCallLogSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            patient = Patient.objects.filter(pk=pk).last()
            obj = AssessmentCallLog.objects.filter(patient=patient)
            serializer = self.serializer_class(obj, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CreateAssessmentCallLogView(APIView):
    serializer_class = AssessmentCallLogSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cm = CareManager.objects.filter(user=request.user).last()
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                obj = serializer.save(care_manager=cm)
                obj.call_duration = datetime.timedelta(minutes=int(request.data['call_duration']))
                obj.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class UpdateAssessmentCallLogView(APIView):
    serializer_class = AssessmentCallLogSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            obj = Patient.objects.get(pk=patient_id)
            return obj
        except Patient.DoesNotExist:
            return None

    def put(self, request, call_log_id, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                call_log = AssessmentCallLog.objects.filter(
                    id=call_log_id, patient=patient
                ).last()
                serializer = self.serializer_class(call_log, data=request.data)
                if serializer.is_valid():
                    obj = serializer.save()
                    obj.call_duration = datetime.timedelta(minutes=int(request.data['call_duration']))
                    obj.save()
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.data,
                        errors=None,
                    )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetAnnualWellnessVisitCallLogView(APIView):
    serializer_class = AnnualWellnessVisitCallLogSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            patient = Patient.objects.get(pk=pk)
            obj = AnnualWellnessVisitCallLog.objects.filter(patient=patient)
            serializer = self.serializer_class(obj, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CreateAnnualWellnessVisitCallLogView(APIView):
    serializer_class = AnnualWellnessVisitCallLogSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cm = CareManager.objects.filter(user=request.user).last()
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                obj = serializer.save(care_manager=cm)
                obj.call_duration = datetime.timedelta(minutes=int(request.data['call_duration']))
                obj.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetSelfManagementPlanCallLogView(APIView):
    serializer_class = SelfManagementPlanCallLogSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            patient = Patient.objects.get(pk=pk)
            obj = SelfManagementPlanCallLog.objects.filter(patient=patient)
            serializer = self.serializer_class(obj, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CreateSelfManagementPlanCallLogView(APIView):
    serializer_class = SelfManagementPlanCallLogSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cm = CareManager.objects.filter(user=request.user).last()
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                obj = serializer.save(care_manager=cm)
                obj.call_duration = datetime.timedelta(minutes=int(request.data['call_duration']))
                obj.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetPatientOutreachView(generics.ListCreateAPIView):
    # renderer_classes = [ApiRenderer, BrowsableAPIRenderer]
    queryset = PatientOutreach.objects.all()
    serializer_class = PatientOutreachSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    filterset_class = PatientOutreachFilter
    search_fields = (
        "notes",
        "contact_date",
        "patient__user__first_name",
    )

    def get_queryset(self, *args, **kwargs):
        qset = super().get_queryset(*args, **kwargs).order_by("-modified_at")
        return qset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request):
        try:
            data = self.filter_queryset(self.get_queryset())
            data = self.paginate_queryset(data)
            serializer = self.serializer_class(
                data, many=True, context={"request": self.request}
            )
            pages = self.get_paginated_response(serializer.data)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=pages.data,
                errors=None,
            )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def post(self, request):
        try:
            caremager_id = request.user.id
            care_manager = CareManager.objects.get(user__id=caremager_id)
            if request.data['recurrence_pattern']:
                if request.data.get('daily'):
                    serializer = RecurrenceDailyOutreachSerializer(data=request.data)
                elif request.data.get('weekly'):
                    serializer = RecurrencWeeklyOutreachSerializer(data=request.data)
                elif request.data.get('monthly'):
                    serializer = RecurrencMonthlyOutreachSerializer(data=request.data)
                elif request.data.get('bi_weekly'):
                    serializer = RecurrencBiWeeklyOutreachSerializer(data=request.data, context={'data': request.data.get('bi_weekly_days')})
                if serializer.is_valid():
                    obj = serializer.save(care_manager=care_manager)
                    obj.time_spent = datetime.timedelta(minutes=int(request.data['time_spent']))
                    obj.save()
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=None,
                        errors=None,
                    )
                else:
                    return create_response_util.create_response_data(
                        message="failed",
                        status=status.HTTP_400_BAD_REQUEST,
                        data=serializer.errors,
                        errors=None,
                    )
            else:
                serializer = self.serializer_class(data=request.data)
                if serializer.is_valid():
                    obj = serializer.save(care_manager=care_manager)
                    obj.time_spent = datetime.timedelta(minutes=int(request.data['time_spent']))
                    obj.save()
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.data,
                        errors=None,
                    )
                else:
                    return create_response_util.create_response_data(
                        message="failed",
                        status=status.HTTP_400_BAD_REQUEST,
                        data=serializer.errors,
                        errors=None,
                    )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PatientOutreachDetailsView(APIView):
    # serializer_class = PatientOutreachSerializer
    permission_classes = [IsAuthenticated]

    # def get_object(self, patient_id):
    #     try:
    #         data = Patient.objects.get(id=patient_id)
    #         return data
    #     except Patient.DoesNotExist:
    #         return None

    def get(self, request, outreach_id):
        try:
            # p_outreach = self.get_object(patient_id)
            #
            # if p_outreach is not None:
            patient_outreach = PatientOutreach.objects.filter(pk=outreach_id).last()
            serializer = PatientOutreachListSerializer(patient_outreach)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class UpdateOutreachView(APIView):
    serializer_class = PatientOutreachUpdateSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, outreach_id):
        try:
            # Check here the date as below after save instance gets also updated
            patient_outreach = PatientOutreach.objects.filter(pk=outreach_id).last()
            serializer = self.serializer_class(patient_outreach, data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                instance.time_spent = datetime.timedelta(minutes=int(request.data['time_spent']))
                instance.save()

                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=serializer.errors,
                    errors=None,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PatientOutreachUpdateView(APIView):
    serializer_class = PatientOutreachSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, outreach_id):
        schedule_date_changed = False
        try:
            # Check here the date as below after save instance gets also updated
            patient_outreach = PatientOutreach.objects.filter(pk=outreach_id).last()
            follow_up_date = request.data.get("schedule_follow_up_date", None)
            if follow_up_date:
                formatted_follow_up_date = datetime.datetime.strptime(
                    follow_up_date, "%Y-%m-%d"
                ).date()
                if patient_outreach.schedule_follow_up_date != formatted_follow_up_date:
                    schedule_date_changed = True

            serializer = self.serializer_class(patient_outreach, data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                instance.time_spent = datetime.timedelta(minutes=int(request.data['time_spent']))
                instance.save()
                """
                    Check if scheduled date has changed in request.data as compared to existing obj;
                    if yes then create a new Outreach
                """
                if schedule_date_changed:
                    create_scheduled_outreach_object(instance)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=serializer.errors,
                    errors=None,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def delete(self, request, pk):
        try:
            p_outreach = self.get_object(pk)
            if p_outreach is not None:
                p_outreach.delete()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CreatePatientContactDetailForCaremanagerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer_patient = CreatepatientforcaremanagerSerializer(
                data=request.data
            )
            if serializer_patient.is_valid():
                cm = CareManager.objects.filter(user=request.user).last()
                user, password = create_patient_user_for_care_manager(
                    request.data, "PATIENT"
                )

                # if request.data.get("caremanager"):
                #     hospital_branch = HospitalBranch.objects.filter(id=request.data.get("caremanager")).last()
                #     serializer_patient.save(user=user, hospital=cm.hospital, caremanager=hospital_branch)

                if request.data.get("caremanager"):
                    cm = CareManager.objects.filter(id=request.data["caremanager"]).last()
                    serializer_patient.save(user=user, hospital=cm.hospital, caremanager_obj=cm)
                else:
                    serializer_patient.save(user=user, hospital=cm.hospital)

                SendMail.send_email_patient_from_caremanager(
                    user, password, hospital_name=cm.hospital.hospital_name
                )
                patient = Patient.objects.filter(user_id=user.id).last()

                communication = request.data.get("communication")
                com = Communication.objects.filter(id=communication)

                patient_contact_detail = PatientContactDetails.objects.create(
                    home_phone=request.data.get("home_phone"),
                    medicaid_id=request.data.get("medicaid_id"),
                    medicare_id=request.data.get("medicare_id"),
                    primary_insurance=request.data.get("primary_insurance"),
                    secondary_email=request.data.get("secondary_email"),
                    cell_phone=request.data.get("cell_phone"),
                    state=request.data.get("state"),
                    zip_code=request.data.get("zip_code"),
                    patient=patient,
                    address_1=request.data.get("address_1"),
                    address_2=request.data.get("address_2"),
                    city=request.data.get("city"),
                    primary_insurance_id=request.data.get("primary_insurance_id"),
                    caremanager=patient.caremanager_obj,
                )
                patient_contact_detail.communication.set(com)

                primary_provider = request.data.get("primary_provider")
                secondary_provider = request.data.get("secondary_provider")

                provider_primary = Provider.objects.filter(id=primary_provider).last()
                provider_secondary = Provider.objects.filter(
                    id=secondary_provider
                ).last()

                patient_provider_mapping = PatientProviderMapping.objects.create(
                    patient=patient,
                    primary_provider=provider_primary,
                    secondary_provider=provider_secondary,
                )

                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=[
                        {"patient_info": serializer_patient.data},
                        {
                            "patient_details": {
                                "home_phone": request.data.get("home_phone"),
                                "medicaid_id": request.data.get("medicaid_id"),
                                "medicare_id": request.data.get("medicare_id"),
                                "primary_insurance": request.data.get(
                                    "primary_insurance"
                                ),
                                "primary_insurance_id": request.data.get("primary_insurance_id"),
                                "secondary_email": request.data.get("secondary_email"),
                                "cell_phone": request.data.get("cell_phone"),
                                "state": request.data.get("state"),
                                "zip_code": request.data.get("zip_code"),
                                "patient": str(patient),
                                "address_1": request.data.get("address_1"),
                                "address_2": request.data.get("address_2"),
                                "city": request.data.get("city"),
                            }
                        },
                        {
                            "provider_mappers": {
                                "primary_provider": str(provider_primary),
                                "secondary_provider": str(provider_secondary),
                            }
                        },
                    ],
                    errors=None,
                )

            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer_patient.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class UpdatePatientContactDetaiForCaremanagerView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, patient_id):
        try:
            patient = Patient.objects.filter(pk=patient_id).last()
            serializer = CreatepatientforcaremanagerSerializer(
                patient, data=request.data
            )
            if serializer.is_valid():
                file = None
                # communication = request.data.get('communication')
                # com = Communication.objects.filter(id=communication)

                caremanager_obj = request.data.get('caremanager')
                caremanager = CareManager.objects.get(id=caremanager_obj)

                if "profile_pic" in request.FILES:
                    file = request.FILES["profile_pic"]
                    fs = FileSystemStorage()
                    file = fs.save(file.name, file)
                user = User.objects.filter(id=patient.user.id).update(
                    email=request.data.get("email"),
                    first_name=request.data.get("first_name"),
                    last_name=request.data.get("last_name"),
                    profile_pic=file,
                )

                patient_contact_detail = PatientContactDetails.objects.filter(
                    patient=patient
                ).update(
                    home_phone=request.data.get("home_phone"),
                    medicaid_id=request.data.get("medicaid_id"),
                    medicare_id=request.data.get("medicare_id"),
                    primary_insurance=request.data.get("primary_insurance"),
                    secondary_email=request.data.get("secondary_email"),
                    cell_phone=request.data.get("cell_phone"),
                    state=request.data.get("state"),
                    zip_code=request.data.get("zip_code"),
                    patient=patient,
                    address_1=request.data.get("address_1"),
                    address_2=request.data.get("address_2"),
                    city=request.data.get("city"),
                    primary_insurance_id=request.data.get("primary_insurance_id"),
                    caremanager=patient.caremanager_obj
                )

                primary_provider = request.data.get("primary_provider")
                secondary_provider = request.data.get("secondary_provider")

                provider_primary = Provider.objects.filter(id=primary_provider).last()
                provider_secondary = Provider.objects.filter(
                    id=secondary_provider
                ).last()

                patient_provider_mapping = PatientProviderMapping.objects.filter(
                    patient=patient
                ).update(
                    primary_provider=provider_primary,
                    secondary_provider=provider_secondary,
                )
                cm = CareManager.objects.filter(id=request.data["caremanager"]).last()
                serializer.save(caremanager_obj=cm)

                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class SendPatientSummaryMailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            data = Patient.objects.get(id=patient_id)
            return data
        except Patient.DoesNotExist:
            return None

    def put(self, request, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                user = User.objects.get(id=patient.user.id)
                files = request.FILES["attachment"]
                data = {
                    "to_mail": user.email,
                    "subject": "Patient Summary Report",
                    "message": "Please Check Summary Report",
                }
                SendMail.send_patient_summary_pdf_mail(data, files)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_400_BAD_REQUEST,
                data=None,
                errors=None,
            )


# inprogress
class UpdatePatientCallLogsstatusView(APIView):
    serializer_class = UpdatePatientOutreachStatusSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, patient_id):
        try:
            patient = Patient.objects.filter(id=patient_id).last()
            objects = PatientOutreach.objects.filter(patient=patient)
            # for obj in objects:
            #     obj. patientoutreach_status =  request.data
            serializer = self.serializer_class(objects, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PatientDetailProviderAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            data = Patient.objects.get(pk=pk)
            return data
        except Patient.DoesNotExist:
            return None

    def get(self, request, pk):
        try:
            patient = self.get_object(pk)
            serializer = PatientDetailSerializer(patient, context={"request": request})
            if patient is not None:
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class ScreeningNameView(APIView):
    serializer = ScreeningNameSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            screening_name = ScreeningName.objects.all()
            serializer = self.serializer(screening_name, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetPatientCallLogWithTypeView(APIView):
    serializer = PatientCallLogWithTypeSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        try:
            patient = Patient.objects.filter(id=patient_id).last()
            serializer = self.serializer(patient, context={"request": request})
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetCareManagerCallLogPatientCount(APIView):
    serializer = CareManagerPatientCountCallLog
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cm = CareManager.objects.filter(user=self.request.user.id).last()
            hospital_care_manager = cm.hospital
            patient = Patient.objects.filter(hospital=cm.hospital)
            zero_to_ten = self.request.query_params.get("0-10")
            eleven_to_nineteen = self.request.query_params.get("11-19")
            above_twenty = self.request.query_params.get("20")
            serializer = self.serializer(
                patient,
                context={
                    "data": patient,
                    "zero_to_ten": zero_to_ten,
                    "eleven_to_nineteen": eleven_to_nineteen,
                    "above_twenty": above_twenty,
                },
            )
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetDefaultCareManagerCallLogPatientCount(APIView):
    serializer = CareManagerPatientDefaultCountCallLog
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cm = CareManager.objects.filter(user=self.request.user.id).last()
            patient = Patient.objects.filter(hospital=cm.hospital, caremanager_obj=cm)
            serializer = self.serializer(cm, context={"data": patient})
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class AnnualWellnessVisitCallLogUpdateApi(APIView):
    serializer_class = AnnualWellnessVisitCallLogSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            obj = Patient.objects.get(pk=patient_id)
            return obj
        except Patient.DoesNotExist:
            return None

    def put(self, request, call_log_id, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                call_log = AnnualWellnessVisitCallLog.objects.filter(
                    id=call_log_id, patient=patient
                ).last()
                serializer = self.serializer_class(call_log, data=request.data)
                if serializer.is_valid():
                    obj = serializer.save()
                    obj.call_duration = datetime.timedelta(minutes=int(request.data['call_duration']))
                    obj.save()
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.data,
                        errors=None,
                    )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetSelfManagementPlanCallLogUpdateView(APIView):
    serializer_class = SelfManagementPlanCallLogSerializer

    # permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            obj = Patient.objects.get(pk=patient_id)
            return obj
        except Patient.DoesNotExist:
            return None

    def put(self, request, call_log_id, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                call_log = SelfManagementPlanCallLog.objects.filter(
                    id=call_log_id, patient=patient
                ).last()
                serializer = self.serializer_class(call_log, data=request.data)
                if serializer.is_valid():
                    obj = serializer.save()
                    obj.call_duration = datetime.timedelta(minutes=int(request.data['call_duration']))
                    obj.save()

                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.data,
                        errors=None,
                    )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class DefaultProblemCreateView(APIView):
    serializer_class = ProblemsCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class DefaultProblemRetrieveView(APIView):
    serializer_class = ProblemsRetrieveSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, problem_id):
        try:
            prblm = Problems.objects.filter(pk=problem_id).last()
            if prblm:
                serializer = self.serializer_class(prblm)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class DefaultProblemUpdateView(APIView):
    serializer_class = ProblemsUpdateSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, problem_id):
        try:
            prblm = Problems.objects.filter(pk=problem_id).last()
            serializer = self.serializer_class(prblm, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class DefaultLoadAllIssuesView(APIView):
    serializer_class = DefaultLoadAllIssuesSerializer

    # permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        try:
            serializer = DefaultLoadAllIssuesSerializer(
                request.data, context={"patient_id": patient_id}
            )
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class DefaultAllergieCreateView(APIView):
    serializer_class = AllergiesCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class DefaultAllergieRetrieveView(APIView):
    serializer_class = AllergiesRetrieveSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, allergie_id):
        try:
            allergie = Allergies.objects.filter(pk=allergie_id).last()
            if allergie:
                serializer = self.serializer_class(allergie)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class DefaultAllergieUpdateView(APIView):
    serializer_class = AllergiesUpdateSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, allergie_id):
        try:
            prblm = Allergies.objects.filter(pk=allergie_id).last()
            serializer = self.serializer_class(prblm, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class DefaultImmunizationCreateView(APIView):
    serializer_class = ImmunizationCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class DefaultImmunizationRetrieveView(APIView):
    serializer_class = ImmunizationRetrieveSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, immunization_id):
        try:
            immunization = Immunization.objects.filter(pk=immunization_id).last()
            if immunization:
                serializer = self.serializer_class(immunization)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class DefaultImmunizationUpdateView(APIView):
    serializer_class = ImmunizationUpdateSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, immunization_id):
        try:
            prblm = Immunization.objects.filter(pk=immunization_id).last()
            serializer = self.serializer_class(prblm, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class DefaultLabReportsCreateView(APIView):
    serializer_class = LabReportsCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class DefaultLabReportsRetrieveView(APIView):
    serializer_class = LabReportsRetrieveSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, labreports_id):
        try:
            lab_reports = LabReports.objects.filter(pk=labreports_id).last()
            if lab_reports:
                serializer = self.serializer_class(lab_reports)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class DefaultLabReportsUpdateView(APIView):
    serializer_class = LabReportsUpdateSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, labreports_id):
        try:
            prblm = LabReports.objects.filter(pk=labreports_id).last()
            serializer = self.serializer_class(prblm, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class DefaultProceduresCreateView(APIView):
    serializer_class = ProceduresCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class DefaultProceduresRetrieveView(APIView):
    serializer_class = ProceduresRetrieveSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, procedures_id):
        try:
            procedures = Procedures.objects.filter(pk=procedures_id).last()
            if procedures:
                serializer = self.serializer_class(procedures)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class DefaultProceduresUpdateView(APIView):
    serializer_class = ProceduresUpdateSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, procedures_id):
        try:
            prblm = Procedures.objects.filter(pk=procedures_id).last()
            serializer = self.serializer_class(prblm, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class DefaultPatientDocsCreateView(APIView):
    serializer_class = PatientDocsCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class DefaultPatientDocsRetrieveView(APIView):
    serializer_class = PatientDocssRetrieveSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, patientdocs_id):
        try:
            patient_docs = PatientDocs.objects.filter(pk=patientdocs_id).last()
            if patient_docs:
                serializer = self.serializer_class(patient_docs)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed ",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class DefaultPatientDocsUpdateView(APIView):
    serializer_class = PatientDocsUpdateSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, patientdocs_id):
        try:
            prblm = PatientDocs.objects.filter(pk=patientdocs_id).last()
            serializer = self.serializer_class(prblm, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class ViewLogsGet(APIView):
    serializer_class = ViewLogsGetSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        try:
            patient = Patient.objects.filter(id=patient_id).last()
            # all_users = ViewLogs.objects.filter(patient=patient).order_by('user__id', '-created_at').distinct('user_id')
            if patient:
                serializer = self.serializer_class(patient)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class ViewLogsCreate(APIView):
    serializer_class = ViewLogsSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = {"patient": request.data["patient"], "user": request.user.id}
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                serializer.save()
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class AuditLogUpdateAPI(APIView):
    def get(self, request, patient_id):
        try:
            related_model = [rel.model for rel in Patient._meta._relation_tree]
            related_model_name = [name.__name__ for name in related_model]
            patient = Patient.objects.filter(id=patient_id).last()
            last_created_at = get_last_updated_object(patient, related_model_name)[0]
            last_modified_at = get_last_updated_object(patient, related_model_name)[1]
            last_created_by = get_last_updated_object(patient, related_model_name)[2]
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data={
                    "last_created_at": last_created_at,
                    "last_modified_at": last_modified_at,
                    "last_created_by": last_created_by,
                },
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class UpdateGoalStatus(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateGoalStatusSerializer

    def get_object(self, goal_id):
        try:
            goal = Goal.objects.filter(id=goal_id).last()
            return goal
        except Goal.DoesNotExist:
            return None

    def put(self, request, goal_id):
        try:
            goal = self.get_object(goal_id)
            if goal is not None:
                serializer = self.serializer_class(goal, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.data,
                        errors=None,
                    )
                else:
                    return create_response_util.create_response_data(
                        message="failed",
                        status=status.HTTP_400_BAD_REQUEST,
                        data=serializer.errors,
                        errors=None,
                    )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CareManagerCallLogPatientDetail(APIView):
    serializer_class = CallLogPatientDetailSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cm = CareManager.objects.filter(user=self.request.user.id).last()
            patient = Patient.objects.filter(hospital=cm.hospital, caremanager_obj=cm)

            # care_manager_hopital_branch = cm.hospital.hospital_branch.filter(care_manager=cm)
            # patient = Patient.objects.filter(hospital=cm.hospital, caremanager__in=care_manager_hopital_branch)
            zero_to_ten = self.request.query_params.get("0-10")
            eleven_to_nineteen = self.request.query_params.get("11-19")
            twenty_to_twenty_nine = self.request.query_params.get("20-29")
            thirty_to_thirty_nine = self.request.query_params.get("30-39")
            more_than_forty = self.request.query_params.get("40")
            serializer = self.serializer_class(
                cm,
                context={
                    "data": patient,
                    "zero_to_ten": zero_to_ten,
                    "eleven_to_nineteen": eleven_to_nineteen,
                    "twenty_to_twenty_nine": twenty_to_twenty_nine,
                    "thirty_to_thirty_nine": thirty_to_thirty_nine,
                    "more_than_forty": more_than_forty
                },
            )
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PatientSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = PatientSessionSerializer(data=request.data)
            cm = CareManager.objects.filter(user=request.user).last()
            if serializer.is_valid():
                number = random.randint(000, 999)
                session_id = f"{timezone.now().strftime('%s')}{number}"
                obj = serializer.save(caremanager=cm, session_id=session_id)
                obj.duration = datetime.timedelta(minutes=int(request.data['duration']))
                obj.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class OutreachAPIView(APIView):
    serializer_class = OutreachSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            search_type = self.request.query_params.get("type")
            if search_type == "patient_name":
                patient = self.request.query_params.get("value")
                term = patient.split()
                if len(term) > 1:
                    patient = PatientOutreach.objects.filter(
                        Q(patient__user__first_name__icontains=term[0])
                        | Q(patient__user__last_name__icontains=term[1])
                    )
                else:
                    patient = PatientOutreach.objects.filter(
                        patient__user__first_name__icontains=patient
                    )

            if search_type == "contact_date":
                date = self.request.query_params.get("value")
                patient = PatientOutreach.objects.filter(contact_date=date)

            if search_type == "schedule_follow_up_date":
                date = self.request.query_params.get("value")
                patient = PatientOutreach.objects.filter(schedule_follow_up_date=date)

            if search_type == "contact_type":
                contact_type = self.request.query_params.get("value")
                patient = PatientOutreach.objects.filter(
                    contact_type__icontains=contact_type
                )

            # if search_type == "resolution_action":
            #     resolution_action = self.request.query_params.get("value")
            #     patient = PatientOutreach.objects.filter(
            #         resolution_action__icontains=resolution_action
            #     )

            if search_type == "outcome":
                outcome = self.request.query_params.get("value")
                patient = PatientOutreach.objects.filter(outcome__icontains=outcome)

            if search_type == "time_spent":
                time_spent = self.request.query_params.get("value")
                patient = PatientOutreach.objects.filter(time_spent=time_spent)

            serializer = self.serializer_class(patient, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class AnnualWellnessVisitLoadWhoView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AWVWhoSerializer

    def list(self, request, *args, **kwargs):
        try:
            objs = AWVWho.objects.all().order_by("name")
            serializer = self.serializer_class(objs, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class AnnualWellnessVisitLoadHowOftenView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AWVHowOftenSerializer

    def list(self, request, *args, **kwargs):
        try:
            objs = AWVHowOften.objects.all().order_by("name")
            serializer = self.serializer_class(objs, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class UpdateGoalTaskStatus(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateTaskStatusSerializer

    def get_object(self, goaltask_id):
        try:
            goaltask = Intervention.objects.filter(id=goaltask_id).last()
            return goaltask
        except goaltask.DoesNotExist:
            return None

    def put(self, request, goaltask_id):
        try:
            goal_task = self.get_object(goaltask_id)
            if goal_task is not None:
                serializer = self.serializer_class(goal_task, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.data,
                        errors=None,
                    )
                else:
                    return create_response_util.create_response_data(
                        message="failed",
                        status=status.HTTP_400_BAD_REQUEST,
                        data=serializer.errors,
                        errors=None,
                    )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class ScreeningWhoOftenView(APIView):
    serializer_class = GetSessionWhoSerializers
    permission_classes = [IsAuthenticated]

    def get(self, request, screening_id):
        try:
            screening = ScreeningWhoOften.objects.filter(id=screening_id).last()
            serializer = self.serializer_class(screening)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CreateMannualTimeView(APIView):
    def post(self, request):
        try:
            serializer = CreateMannualTimeSerializer(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetCreateCareManagerTaskView(generics.ListCreateAPIView):
    serializer_class = CareManagerTaskSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            caremaager_id = request.user.id
            care_manager = CareManager.objects.get(user__id=caremaager_id)
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                obj = serializer.save(care_manager=care_manager)
                obj.time_spent = datetime.timedelta(minutes=int(request.data['time_spent']))
                obj.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetPatientOutreachTaskView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = CareManager.objects.filter(user=self.request.user).last()
        queryset = taskoutreachsearch(self, queryset)
        return queryset

    def list(self, request):
        try:
            cm = self.get_queryset()
            if cm:
                cm = self.paginate_queryset(cm)
                pages = self.get_paginated_response(cm)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=pages.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=[],
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class TaskDetailUpdateView(APIView):
    serializer_class = TaskDetailUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        try:
            cm = CareManager.objects.filter(user=self.request.user).last()
            task = Task.objects.filter(care_manager=cm, id=task_id)
            serializer = self.serializer_class(task, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def put(self, request, task_id):
        try:
            cm = CareManager.objects.filter(user=self.request.user).last()
            task = Task.objects.filter(care_manager=cm, id=task_id).last()
            serializer = self.serializer_class(task, data=request.data)
            if serializer.is_valid():
                obj = serializer.save()
                obj.time_spent = datetime.timedelta(minutes=int(request.data['time_spent']))
                obj.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetGeneralNotesCallLogView(APIView):
    serializer_class = GeneralNotesCallLogSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            patient = Patient.objects.get(pk=pk)
            obj = GeneralNotesCallLog.objects.filter(patient=patient)
            serializer = self.serializer_class(obj, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CreateGeneralNotesCallLogView(APIView):
    serializer_class = GeneralNotesCallLogSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cm = CareManager.objects.filter(user=request.user).last()
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save(care_manager=cm)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GeneralNotesCallLogUpdateApi(APIView):
    serializer_class = GeneralNotesCallLogSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            obj = Patient.objects.get(pk=patient_id)
            return obj
        except Patient.DoesNotExist:
            return None

    def put(self, request, call_log_id, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                call_log = GeneralNotesCallLog.objects.filter(
                    id=call_log_id, patient=patient
                ).last()
                serializer = self.serializer_class(call_log, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.data,
                        errors=None,
                    )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PatientTaskOutreachCallLogList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    filterset_class = PatientFilter

    def get_queryset(self, *args, **kwargs):
        cm = CareManager.objects.filter(user=self.request.user.id).last()
        patient_id = self.kwargs["patient_id"]
        queryset = taskoutreachcalllog_combine(self, cm, patient_id)
        return queryset

    def list(self, request, patient_id):
        try:
            patient = self.get_queryset(patient_id=patient_id)
            if patient:
                data = self.paginate_queryset(patient)
                pages = self.get_paginated_response(data)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=pages.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=[],
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class problemsListView(generics.ListAPIView):
    serializer_class = ProblemsRetrieveSerializer
    permission_classes = [IsAuthenticated]
    # filter_backends = (
    #     SearchFilter,
    #     DjangoFilterBackend,
    # )
    # filterset_class = FilterData
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    search_fields = ("name", "description")

    def get_queryset(self, *args, **kwargs):
        patient_id = self.kwargs.get("patient_id")
        queryset = Problems.objects.filter(patient_id=patient_id)
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, patient_id):
        try:
            problems = self.filter_queryset(self.get_queryset(patient_id=patient_id))
            serializer = self.serializer_class(problems, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class AllergiesListView(generics.ListAPIView):
    serializer_class = AllergiesRetrieveSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    search_fields = ("name", "description")

    # filterset_class = FilterData

    def get_queryset(self, *args, **kwargs):
        patient_id = self.kwargs.get("patient_id")
        queryset = Allergies.objects.filter(patient_id=patient_id)
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, patient_id):
        try:
            allergies = self.filter_queryset(self.get_queryset(patient_id=patient_id))
            serializer = self.serializer_class(allergies, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class ImmunizationListView(generics.ListAPIView):
    serializer_class = ImmunizationRetrieveSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    search_fields = ("name", "description")

    # filterset_class = FilterData

    def get_queryset(self, *args, **kwargs):
        patient_id = self.kwargs.get("patient_id")
        queryset = Immunization.objects.filter(patient_id=patient_id)
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, patient_id):
        try:
            immunization = Immunization.objects.filter(patient_id=patient_id)
            serializer = self.serializer_class(immunization, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class LabreportsListView(generics.ListAPIView):
    serializer_class = LabReportsRetrieveSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    search_fields = ("name", "description")

    # filterset_class = FilterData

    def get_queryset(self, *args, **kwargs):
        patient_id = self.kwargs.get("patient_id")
        queryset = LabReports.objects.filter(patient_id=patient_id)
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, patient_id):
        try:
            labReports = self.filter_queryset(self.get_queryset(patient_id=patient_id))
            serializer = self.serializer_class(labReports, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PatientDocListView(generics.ListAPIView):
    serializer_class = PatientDocssRetrieveSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    search_fields = ("name", "description")

    # filterset_class = FilterData

    def get_queryset(self, *args, **kwargs):
        patient_id = self.kwargs.get("patient_id")
        queryset = PatientDocs.objects.filter(patient_id=patient_id)
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, patient_id):
        try:
            patientdocs = self.filter_queryset(self.get_queryset(patient_id=patient_id))
            serializer = self.serializer_class(patientdocs, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class ProceduresListView(generics.ListAPIView):
    serializer_class = ProceduresRetrieveSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    search_fields = ("name", "description")

    # filterset_class = FilterData

    def get_queryset(self, *args, **kwargs):
        patient_id = self.kwargs.get("patient_id")
        queryset = Procedures.objects.filter(patient_id=patient_id)
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, patient_id):
        try:
            procedures = self.filter_queryset(self.get_queryset(patient_id=patient_id))
            serializer = self.serializer_class(procedures, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetSessionTimeList(generics.ListAPIView):
    serializer_class = SessionTimeSerializer
    permission_classes = [IsAuthenticated]

    # filter_backends = (
    #     SearchFilter,
    #     DjangoFilterBackend,
    # )
    # search_fields = FilterSession

    def get_queryset(self, *args, **kwargs):
        patient_id = self.kwargs.get("patient_id")
        queryset = Patient.objects.filter(id=patient_id).last()
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, patient_id):
        try:
            patient = self.filter_queryset(self.get_queryset(patient_id=patient_id))
            # patient = self.get_queryset(patient_id=patient_id)
            serializer = self.serializer_class(patient, context={"request": request})
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetCMTwentyMinCallLogPatientCount(APIView):
    serializer = CMTwentyMinCallLogPatientCountSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cm = CareManager.objects.filter(user=self.request.user.id).last()
            patient = Patient.objects.filter(hospital=cm.hospital, caremanager_obj=cm)
            serializer = self.serializer(patient, context={"data": patient})
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CreateCareManagerNotesView(APIView):
    serializer_class = CareManagerNotesSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            caremanager_id = request.user.id
            care_manager = CareManager.objects.get(user__id=caremanager_id)
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                obj = serializer.save(care_manager=care_manager)
                obj.time_spent = datetime.timedelta(minutes=int(request.data['time_spent']))
                obj.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=serializer.errors,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CareManagerNotesDetailUpdateView(APIView):
    serializer_class = CareManagerDetailUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, cm_notes_id):
        try:
            cm = CareManager.objects.filter(user=self.request.user).last()
            task = CareManagerNotes.objects.filter(care_manager=cm, id=cm_notes_id)
            serializer = self.serializer_class(task, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def put(self, request, cm_notes_id):
        try:
            cm = CareManager.objects.filter(user=self.request.user).last()
            task = CareManagerNotes.objects.filter(care_manager=cm, id=cm_notes_id).last()
            serializer = self.serializer_class(task, data=request.data)
            if serializer.is_valid():
                obj = serializer.save()
                obj.time_spent = datetime.timedelta(minutes=int(request.data['time_spent']))
                obj.save()
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class ShowPatientDurationStatsView(APIView):
    serializer = ShowPatientDurationStatsSerializer
    queryset = Patient.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cm = CareManager.objects.filter(user=request.user).last()
            serializer = self.serializer(cm)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class TaskHistoryListView(generics.ListAPIView):
    serializer_class = TaskHistoryListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    search_fields = ("task_date", "notes", "time_spent", "task_status", "resolution_action")
    filterset_class = TaskFilter

    def get_queryset(self, *args, **kwargs):
        patient_id = self.kwargs.get("patient_id")
        caremanager = CareManager.objects.filter(user=self.request.user).last()

        queryset = Task.objects.filter(care_manager=caremanager, patient__id=patient_id)
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, patient_id):
        try:
            cm = self.filter_queryset(self.get_queryset(patient_id=patient_id))
            data = self.paginate_queryset(cm)
            serializer = self.serializer_class(data, many=True)
            pages = self.get_paginated_response(serializer.data)
            # return Response(pages.data)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=pages.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class OutreachHistoryListView(generics.ListAPIView):
    serializer_class = OutreachHistoryListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    search_fields = ("notes", "time_spent", "outreach_status", "contact_type", "schedule_follow_up_date")
    filterset_class = PatientOutreachFilter

    def get_queryset(self, *args, **kwargs):
        patient_id = self.kwargs.get("patient_id")
        caremanager = CareManager.objects.filter(user=self.request.user).last()
        queryset = PatientOutreach.objects.filter(care_manager=caremanager, patient__id=patient_id)
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, patient_id):
        try:
            cm = self.filter_queryset(self.get_queryset(patient_id=patient_id))
            data = self.paginate_queryset(cm)
            serializer = self.serializer_class(data, many=True)
            pages = self.get_paginated_response(serializer.data)
            # return Response(pages.data)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=pages.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class CareManagerNotesHistoryListView(generics.ListAPIView):
    serializer_class = CareManagerNotesHistoryListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    search_fields = ("caremanager_notes_date", "notes", "time_spent")

    def get_queryset(self, *args, **kwargs):
        patient_id = self.kwargs.get("patient_id")
        caremanager = CareManager.objects.filter(user=self.request.user).last()
        queryset = CareManagerNotes.objects.filter(care_manager=caremanager, patient__id=patient_id)
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, patient_id):
        try:
            cm = self.filter_queryset(self.get_queryset(patient_id=patient_id))
            data = self.paginate_queryset(cm)
            serializer = self.serializer_class(data, many=True)
            pages = self.get_paginated_response(serializer.data)
            # return Response(pages.data)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=pages.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetUnAssignProviderPatient(generics.ListAPIView):
    serializer_class = UnassignProviderPatientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (UnAssignProviderPatientSearch, DjangoFilterBackend,)

    def get_queryset(self, *args, **kwargs):
        provider=Provider.objects.get(id=self.kwargs["provider_id"])
        cm = CareManager.objects.filter(user=self.request.user.id).last()
        unassign_patient_queryset = Patient.objects.filter(caremanager_obj=cm, hospital=cm.hospital).exclude(patient_patientprovidermapping__primary_provider=provider.id)
        return unassign_patient_queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
                queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, provider_id):
        try:
            unassign_patient = self.filter_queryset(self.get_queryset(request))
            unassign_patient_pagination = self.paginate_queryset(unassign_patient)
            serializer = self.serializer_class(unassign_patient_pagination, many=True)
            pages = self.get_paginated_response(serializer.data)
            # return Response(pages.data)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=serializer.data,
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )
