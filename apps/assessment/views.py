import datetime
import json
from django.utils import timezone
from apps.account_manager.models import Patient

from rest_framework import status
from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend

from apps.account_manager import create_response_util
from apps.assessment.models import AppointmentSchedule, SelfManagementPlan, Question, AssessmentQuestionCategory, \
    Assessment, PatientQuestionAnswer
from apps.assessment.serializers import (
    AppointmentScheduleSerializer,
    CreatePatientQuestionAnswerCreateSerializer,
    CreatePatientQuestionAnswerSerializer,
    SelfManagementPlanSerializer,
    GetQuestionSerializer,
    AssessmentQuestionListSerializer,
    AssessmentQuestionCategorySerializer,
    CreateAssessmentSerializer,
    PatientQuestionAnswerSerializer, CreateAssessmentStatusSerializer, ListAssessmentSerializer,
    PatientAnswerUpdateSerializer,
    UpdateAssessmentMannualTimeViewSerializer
)


from apps.patient.models import Task
from apps.assessment.utils import AssessmentFilter


class AppointmentScheduleView(APIView):
    """
    List all appointments and create new appointment
    """
    serializer = AppointmentScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = AppointmentSchedule.objects.all()
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
            serializer = AppointmentScheduleSerializer(data=request.data)
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


class AppointmentScheduleDetailsView(APIView):
    """
    Get, Update and Delete Appointment
    """
    serializer = AppointmentScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            data = AppointmentSchedule.objects.filter(id=id)
            serializer = self.serializer(data, many=True)
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

    def put(self, request, id):
        try:
            data = AppointmentSchedule.objects.get(id=id)
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
            profile = AppointmentSchedule.objects.filter(id=id)
            if profile.exists():
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


class AppointmentListView(APIView):
    serializer = AppointmentScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            now = timezone.now()
            params = self.request.query_params
            event_type = params.get("event_type")

            if event_type == "upcoming_appointment":
                upcoming_appointment = AppointmentSchedule.objects.filter(
                    appointment_date_time__gt=now
                ).order_by("appointment_date_time")
                serializer = self.serializer(upcoming_appointment, many=True)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )

            elif event_type == "due_appointment":
                due_appointment = AppointmentSchedule.objects.filter(
                    appointment_date_time__lt=now
                ).order_by("-appointment_date_time")
                serializer = self.serializer(due_appointment, many=True)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )

            else:
                all_appointment = AppointmentSchedule.objects.all()
                serializer = self.serializer(all_appointment, many=True)
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


class SelfManagementPlanView(APIView):
    """
    create and get all description and note of patient
    """
    serializer = SelfManagementPlanSerializer
    queryset = SelfManagementPlan.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = SelfManagementPlan.objects.all()
            serializer = self.serializer(data, many=True)
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
            serializer = SelfManagementPlanSerializer(data=request.data)
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


class SelfManagementPlanDetailsView(APIView):
    """
    get, update and delete description and note of patient
    """
    serializer = SelfManagementPlanSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            data = SelfManagementPlan.objects.filter(id=id).last()
            serializer = self.serializer(data)
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

    def put(self, request, id):
        try:
            obj = SelfManagementPlan.objects.filter(id=id).last()
            serializer = self.serializer(obj, data=request.data)
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
            profile = SelfManagementPlan.objects.filter(id=id).last()
            if profile.exists():
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


class GetPatientDetailsView(APIView):
    serializer = SelfManagementPlanSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            patient_id = SelfManagementPlan.objects.filter(pk=pk)
            serializer = self.serializer(patient_id, many=True)
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


class AssessmentQuestionListView(APIView):
    serializer_class = AssessmentQuestionListSerializer

    def get_queryset(self, request):
        queryParams = self.request.GET.get('question_category')  # get queryparameter from url
        if queryParams is None:
            queryset = Question.objects.all()
        else:
            queryset = Question.objects.filter(question_category__question_category=queryParams)
        return queryset

    def get(self, request):
        try:
            queryset = self.get_queryset(request)
            questions_count = queryset.count()
            serializer = self.serializer_class(queryset, many=True)
            data = {
                "questions_count": questions_count,
                "question_answer": serializer.data
            }
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=data,
                errors=None,
            )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class AssessmentQuestionCategoryView(APIView):
    serializer_class = AssessmentQuestionCategorySerializer

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

    def get(self, request):
        try:
            data = AssessmentQuestionCategory.objects.all()
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


class GetQuestionView(APIView):
    serializer_class = GetQuestionSerializer

    def get(self, request, category_id):
        try:
            question_category = AssessmentQuestionCategory.objects.filter(id=category_id).last()
            # data = Question.objects.filter(question_category=question_category)
            data=Question.objects.filter(question_category=question_category).exclude(option_1=None,option_2=None,option_3=None,option_4=None,option_5=None).order_by("id")
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


class CreateAssessmentView(generics.ListAPIView):
    serializer_class = CreateAssessmentSerializer
    pagination_class = PageNumberPagination
    queryset = Assessment.objects.filter(is_active=True)
    filter_backends = (SearchFilter, DjangoFilterBackend,)
    filterset_class = AssessmentFilter

    def get_queryset(self, *args, **kwargs):
        qset = super().get_queryset(*args, **kwargs)
        return qset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset
    
    ##
    def list(self, request):
        try:
            assessment_data = self.filter_queryset(self.get_queryset())
            data = self.paginate_queryset(assessment_data)
            serializer = self.serializer_class(data, many=True)
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

    ##
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                data = serializer.save(start_date=timezone.now(), is_active=False)
                if data.manual_time:
                    data.manual_time = datetime.timedelta(minutes=int(request.data['manual_time']))
                else:
                    data.manual_time = datetime.timedelta(minutes=0)
                data.save()
                PatientQuestionAnswer.objects.filter(patient=data.patient, is_active = False).update(assessment= data.id, is_active = True)
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


class GetPatientAssessmentView(APIView):

    serializer_class = ListAssessmentSerializer

    ##
    def get(self, request, patient_id):
        try:
            patient = Patient.objects.filter(id=patient_id).last()
            assessment = Assessment.objects.filter(patient=patient, is_active = True)
            serializer = self.serializer_class(assessment, many=True)
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

class PatientAssessmentUpdateView(APIView):

    serializer_class = CreateAssessmentSerializer

    def put(self, request, patient_id):
        try:
            patient = Patient.objects.filter(id=patient_id).last()
            if patient is not None:
                assessment = Assessment.objects.filter(patient=patient).last()
                serializer = self.serializer_class(assessment, data=request.data)
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
                    data="Patient Not Found",
                    errors=None,
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

class PatientQuestionAnswerView(APIView):
    serializer_class = CreatePatientQuestionAnswerCreateSerializer

    # def post(self, request):
    #     try:
    #         serializer = self.serializer_class(data=request.data, many=True)
    #         if serializer.is_valid():
    #             serializer.save()
    #             for data in request.data:
    #                 assessment_id = data.get('assessment')
    #                 Assessment.objects.filter(id=assessment_id).update(is_active=True)
                
    #             return create_response_util.create_response_data(
    #                 message="success",
    #                 status=status.HTTP_200_OK,
    #                 data=serializer.data,
    #                 errors=None,
    #             )
    #         else:
    #             return create_response_util.create_response_data(
    #                 message="failed",
    #                 status=status.HTTP_400_BAD_REQUEST,
    #                 data=None,
    #                 errors=serializer.errors,
    #             )
    #     except Exception as e:
    #         return create_response_util.create_response_data(
    #             message="failed",
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             data=None,
    #             errors=str(e),
    #         )
    
    ##
    def post(self, request):
        try:
            # question_category_id = request.data.get('question_category')
            # score = request.data.get('score')
            
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                patient_question_answer_data =  request.data.pop('patient_question_answer')
                patient_question_answer_serializer = CreatePatientQuestionAnswerSerializer(data=patient_question_answer_data, many=True)
                if patient_question_answer_serializer.is_valid():
                    data = patient_question_answer_serializer.save(is_active = False)
                    # question_category_obj = AssessmentQuestionCategory.objects.filter(id=question_category_id).last()
                    # patient_id = data[0].patient
                    # QuestionScore.objects.create(question_category=question_category_obj,score=score,patient=patient_id)
                
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
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetPatientQuestionAnswerView(APIView):
    serializer_class = PatientQuestionAnswerSerializer

    def get(self, request, patient_id):
        try:
            patient = Patient.objects.filter(id=patient_id).last()
            assessment = PatientQuestionAnswer.objects.filter(patient=patient)
            serializer = self.serializer_class(assessment, many=True)
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


class GetAssessmentPatiantDataView(APIView):
    serializer_class = PatientQuestionAnswerSerializer

    def get(self, request, assessment_id, patient_id):
        try:
            assessment = PatientQuestionAnswer.objects.filter(assessment__id=assessment_id, patient__id=patient_id).order_by("id")
            serializer = self.serializer_class(assessment, many=True, context={'assessment_id': assessment_id})
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

    ##
    def put(self, request, assessment_id, patient_id):
        try:
            assesment = Assessment.objects.filter(id=assessment_id, patient=patient_id).last()
            serializer = CreateAssessmentStatusSerializer(assesment, data=request.data)
            if serializer.is_valid():
                assesment_start_datetime = assesment.start_date
                duration = timezone.now() - assesment_start_datetime
                serializer.save(time_spent=duration, end_date=timezone.now(), assessment_status="COMPLETED", is_active=True)
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


class PatientAnswerUpdateView(APIView):
    """
    Update Patient Answers
    """
    serializer = PatientAnswerUpdateSerializer
    # permission_classes = [IsAuthenticated]

    ##
    def put(self, request, question_id):
        try:
            assessment_id = request.data.get("assessment")
            pcd_obj = PatientQuestionAnswer.objects.filter(question=question_id,assessment=request.data.get('assessment'),patient=request.data.get('patient')).last()
            serializer = self.serializer(pcd_obj, data=request.data)
            if serializer.is_valid():
                serializer.save()
                Assessment.objects.filter(id=assessment_id).update(score=request.data.get("score"), severity=request.data.get("severity"), action_taken=request.data.get("action_taken") )
                data = Assessment.objects.filter(id=assessment_id).last()
                if data.manual_time:
                    data.manual_time = datetime.timedelta(minutes=int(request.data['manual_time']))
                else:
                    data.manual_time = datetime.timedelta(minutes=0)
                data.save()
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
                        errors="No Data Found",
                    )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )



class UpdateAssessmentMannualTimeView(APIView):
    """
    Update Patient Manual time and action taken
    """
    serializer = UpdateAssessmentMannualTimeViewSerializer

    ##
    def put(self, request):
        try:
            assessment = Assessment.objects.filter(id=request.data.get('assessment'),patient=request.data.get('patient')).last()
            serializer = self.serializer(assessment, data=request.data)
            if serializer.is_valid():
                data = serializer.save()
                if data.manual_time:
                    data.manual_time = datetime.timedelta(minutes=int(request.data['manual_time']))
                else:
                    data.manual_time = datetime.timedelta(minutes=0)
                data.save()
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
                        errors="No Data Found",
                    )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )