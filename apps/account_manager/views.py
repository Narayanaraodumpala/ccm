from datetime import date
from http import HTTPStatus

from apps.account_manager.serializers import MultiSerializers

from datetime import datetime
from datetime import date

import pandas as pd
import os
import datetime as dt
from datetime import timedelta
import xlwt
import uuid
from django.db.models import Q
from django.contrib.auth import get_user_model
from apps.patient.models import Allergies, Goal, Immunization, Intervention, PatientOutreach, Procedures, \
    ProgramInformation, Task
from django_filters import filters
from django_filters.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from django.db.models import Value
from django.db.models.functions import Concat

from apps.account_manager import create_response_util
from apps.account_manager.admin import PatientResource, ProviderResource
from apps.account_manager.create_response_util import ApiRenderer
from apps.account_manager.utils import AssignProviderPatientSearch, create_related_user, create_provider_user, \
    create_provider_user_for_care_manager, SendMail, PatientListFilter, ProviderFilter, PatientSearchFilter
from apps.account_manager.serializers import AssignPatientListSerializer, CaremanagerPatientCountSerializer, \
    ChronicConditionPatientCountSerializer, GetHospitalCareManagerSerializer, PatientSerializer, \
    CaremanagerPatientProfileSerializer
from apps.account_manager.serializers import CaremanagerPatientCountSerializer, ChronicConditionPatientCountSerializer, \
    GetCareManagerlistSerializer, GetHospitalCareManagerSerializer, PatientSerializer, \
    CaremanagerPatientProfileSerializer, MultiplePatientSerializer, ProviderPatientCountSerializer, \
    ProviderUpdateSerializer, ChronicPatientCountSerializer, PatientStatsTotalPatientSerializer
from apps.account_manager.models import CareManager, PatientContactDetails, PracticeAdmin, Patient, Provider, \
    PatientProviderMapping
from apps.account_manager.serializers import (
    CareManagerSerializer,
    PracticeAdminSerializer,
    ProviderSerializer,
    CareManagerProviderSerializer,
    PatientListForCareManagerSerializer, ProviderCreateSerializer, GetCareManagerListSerializer,
    CareManagerPatientSerializer, PatientListForCareManagerSerializer, CaremanagerTaskOutreachListSerializer,
    GetCaremanagerPracticeSerializer

)

from apps.hospital.models import Hospital, ChronicCondition, HospitalBranch, Medication
from apps.patient.models import PatientCallLog
from apps.patient.serializers import CareManagerCompletedMinsSerializer

from apps.patient.serializers import PatientCallLogSerializer

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend

from apps.patient.utils import CustomPageNumberPagination
from revision_be import settings

from datetime import timedelta

from apps.patient.models import PatientCallLog
from apps.patient.serializers import CareManagerCompletedMinsSerializer

from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper
import mimetypes

User = get_user_model()


class CareManagerApiView(generics.ListAPIView):
    serializer_class = CareManagerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (SearchFilter, DjangoFilterBackend,)
    search_fields = ['user__first_name']

    pagination_class = PageNumberPagination

    def get_queryset(self, *args, **kwargs):
        queryset = CareManager.objects.all()
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request):
        try:
            cm = self.filter_queryset(self.get_queryset(request))
            care_managers = self.paginate_queryset(cm)
            serializer = self.serializer_class(care_managers, many=True)
            pages = self.get_paginated_response(serializer.data)
            # return Response(serializer.data)
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
            hospital_id = request.data.get('hospital')
            data = request.data
            serializer = CareManagerSerializer(
                data=data, context={'request': request})
            if serializer.is_valid():
                user = create_related_user(request.data, "CAREMANAGER")
                care_manager = serializer.save(user=user)
                hospital_branches = request.data.get('hospital_branch')
                if hospital_branches:
                    for hospital_branch in hospital_branches:
                        HospitalBranch.objects.filter(
                            pk=hospital_branch).update(care_manager=care_manager)
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.data,
                        errors=None,
                    )
                SendMail.user_send_credential_email(
                    user, password=request.data["password"])
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


class CareManagerRetriveApiView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CareManagerSerializer

    def get(self, request, id):
        try:
            caremanager = CareManager.objects.filter(id=id).last()
            if caremanager is not None:
                serializer = self.serializer_class(caremanager)
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
            data = request.data
            caremanager = CareManager.objects.get(id=id)
            serializer = self.serializer_class(caremanager, data=data)
            if serializer.is_valid():
                serializer.save()
                user = User.objects.get(id=caremanager.user.id)
                user.email = data["email"]
                user.first_name = data["first_name"]
                user.last_name = data["last_name"]
                user_password = data["password"]
                user.set_password(user_password)
                user.save()
                SendMail.user_upadte_credential_email(
                    user, password=request.data["password"])

                hospital_branches = request.data.get('hospital_branch')
                if hospital_branches:
                    for hospital_branch in hospital_branches:
                        HospitalBranch.objects.filter(
                            pk=hospital_branch).update(care_manager=caremanager)
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.data,
                        errors=None,
                    )
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    errors=None,
                    data=serializer.data,
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
            caremanager = CareManager.objects.get(id=id)
            if caremanager:
                caremanager.is_active = False
                caremanager.save()
                user = User.objects.get(id=caremanager.user.id)
                user.is_active = False
                user.save()
                return create_response_util.create_response_data(
                    message="success", status=status.HTTP_200_OK, data=None, errors=None
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


class PracticeAdminCreateApiView(APIView):
    serializer_class = PracticeAdminSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination()

    def get(self, request, format=None):
        try:
            obj = PracticeAdmin.objects.all().order_by('-id')
            if obj:
                practice_admins = self.pagination_class.paginate_queryset(
                    obj, request)
                serializer = self.serializer_class(practice_admins, many=True)
                pages = self.pagination_class.get_paginated_response(
                    serializer.data)

                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=pages.data,
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
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                user = create_provider_user(request.data, "PRACTICEADMIN")
                serializer.save(user=user)
                SendMail.user_send_credential_email(
                    user, password=request.data["password"])    
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


class PracticeAdminRetriveApiView(APIView):
    serializer_class = PracticeAdminSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            practice_admin = PracticeAdmin.objects.filter(id=id).last()
            if practice_admin:
                serializer = self.serializer_class(practice_admin)

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
            data = request.data
            practice_admin = PracticeAdmin.objects.get(id=id)
            serializer = self.serializer_class(practice_admin, data=data)
            if serializer.is_valid():
                serializer.save()
                user = User.objects.get(id=practice_admin.user.id)
                user.email = data["email"]
                user.first_name = data["first_name"]
                user.last_name = data["last_name"]
                user_password = data["password"]
                user.set_password(user_password)
                user.save()
                SendMail.user_upadte_credential_email(user,password=request.data["password"])
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
            practice_admin = PracticeAdmin.objects.get(id=id)
            if practice_admin:
                practice_admin.is_active = False
                practice_admin.save()
                user = User.objects.get(id=practice_admin.user.id)
                user.is_active = False
                user.save()
                return create_response_util.create_response_data(
                    message="success", status=status.HTTP_200_OK, data=None, errors=None
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


class ProviderAPIView(APIView):
    serializer_class = ProviderSerializer
    # permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination()

    def get_queryset(self, request):
        queryset = Provider.objects.all().order_by('-created_at')
        sort_by = request.GET.get('sort_by')
        if sort_by == "department":
            queryset = queryset.order_by("department__name")
            return queryset
        return queryset

    def get(self, request):
        try:
            provider = self.get_queryset(request)
            if provider:
                providers = self.pagination_class.paginate_queryset(
                    provider, request)
                serializer = self.serializer_class(providers, many=True)
                pages = self.pagination_class.get_paginated_response(
                    serializer.data)

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

            hospital_id = request.data.get('hospital')
            data = request.data
            serializer = ProviderCreateSerializer(
                data=data, context={'request': request})
            if serializer.is_valid():
                user = create_provider_user(data, "PROVIDER")
                provider = serializer.save(user=user)
                hospital_branches = request.data.get('hospital_branch')
                if hospital_branches:
                    for hospital_branch in hospital_branches:
                        HospitalBranch.objects.filter(pk=hospital_branch).update(
                            provider=provider, hospital=hospital_id)
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.data,
                        errors=None,
                    )
                else:
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


class ProviderDetailUpdateView(APIView):
    serializer_class = ProviderSerializer

    # permission_classes = [IsAuthenticated]

    def get(self, request, provider_id):
        try:
            provider = Provider.objects.filter(id=provider_id).last()
            if provider:
                serializer = self.serializer_class(provider)
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

    def put(self, request, provider_id):
        try:
            hospital_branches = request.data.get('hospital_branch')
            hospital_id = request.data.get('hospital')
            data = request.data
            provider = Provider.objects.get(id=provider_id)
            serializer = ProviderUpdateSerializer(provider, data=data)
            if serializer.is_valid():
                serializer.save()
                user = User.objects.get(id=provider.user.id)
                user.email = data["email"]
                user.first_name = data["first_name"]
                user.last_name = data["last_name"]
                user_password = data["password"]
                user.set_password(user_password)
                user.save()
                SendMail.user_upadte_credential_email(user,password=request.data["password"])
                if hospital_branches:
                    # HospitalBranch.objects.filter(provider=provider).update(provider=None)
                    for hospital_branch in hospital_branches:
                        HospitalBranch.objects.filter(
                            pk=hospital_branch).update(provider=provider)
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.data,
                        errors=None,
                    )
                else:
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


class SearchPatientAPIView(APIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name", "birth_date"]

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get(self, request, *args, **kwargs):
        try:
            base_qs = Patient.objects.all()
            filtered_qs = self.filter_queryset(base_qs)
            serializer = PatientSerializer(filtered_qs, many=True)
            if serializer.is_valid():
                return create_response_util.create_response_data(
                    message="success", status=status.HTTP_200_OK, data=None, errors=None
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


class CountProviderCareManagerPatientApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            provider_total_count = Provider.objects.all().count()
            care_manager_total_count = CareManager.objects.all().count()
            patient_total_count = Patient.objects.all().count()
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data={
                    "provider_total_count": provider_total_count,
                    "care_manager_total_count": care_manager_total_count,
                    "patient_total_count": patient_total_count,
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


class CareManagerProviderApiView(generics.ListCreateAPIView):
    serializer_class = CareManagerProviderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = (SearchFilter, DjangoFilterBackend,)
    filterset_class = ProviderFilter
    search_fields = ('user__first_name', 'user__last_name', 'created_at')

    def get_queryset(self, *args, **kwargs):
        cm = CareManager.objects.filter(user=self.request.user.id).last()
        hospital_care_manager = cm.hospital
        queryset = Provider.objects.filter(hospital=hospital_care_manager).exclude(
            provider_status="SUSPENDED").order_by("-modified_at")
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request):
        try:
            provider = self.filter_queryset(self.get_queryset())
            data = self.paginate_queryset(provider)
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

    def post(self, request):
        try:
            cm = CareManager.objects.filter(user=request.user.id).last()
            hospital_care_manager = cm.hospital
            serializer = CareManagerProviderSerializer(data=request.data)
            if serializer.is_valid():
                user, password = create_provider_user_for_care_manager(
                    request.data, "PROVIDER")
                serializer.save(user=user, hospital=hospital_care_manager)
                SendMail.send_welcome_email_provider_from_caremanager(user)
                SendMail.send_credential_email_provider_from_caremanager(
                    user, password)

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


class OutreachProviderGetApi(APIView):
    serializer_class = CareManagerProviderSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cm = CareManager.objects.filter(user=self.request.user.id).last()
            hospital_care_manager = cm.hospital
            all_providers = Provider.objects.filter(
                hospital=hospital_care_manager)
            serializer = self.serializer_class(all_providers, many=True)
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


class CareManagerProviderDetailApiView(APIView):
    serializer_class = CareManagerProviderSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, provider_id):
        try:
            provider = Provider.objects.filter(pk=provider_id).last()
            serializer = self.serializer_class(provider)
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

    def put(self, request, provider_id):
        try:
            provider = Provider.objects.filter(pk=provider_id).last()
            data = request.data
            serializer = self.serializer_class(provider, data)
            if serializer.is_valid():
                serializer.save()
                user = User.objects.get(id=provider.user.id)
                user.email = data["email"]
                user.first_name = data["first_name"]
                user.last_name = data["last_name"]
                user.profile_pic = data["profile_pic"]
                user.save()
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


# class PatientListForCareManagerApiView(generics.ListCreateAPIView):
#     renderer_classes = [ApiRenderer, BrowsableAPIRenderer]

#     permission_classes = [AllowAny]
#     queryset = Patient.objects.all()
#     serializer_class = PatientListForCareManagerSerializer
#     filter_backends = (DjangoFilterBackend,)

#     filterset_class = MyFilter

#     def get_queryset(self,*args, **kwargs):
#         qset = super().get_queryset(*args, **kwargs)

#         return qset

#     def filter_queryset(self, queryset):
#         for backend in list(self.filter_backends):
#             queryset = backend().filter_queryset(self.request, queryset, self)
#         return queryset

#     def list(self, request):
#         try:
#             all_pts = self.filter_queryset(self.get_queryset())

#             # all_pts = self.filter_queryset(qs)

#             # all_pts = self.filter_queryset()
#             # all_pts = Patient.objects.all()
#             serializer = self.serializer_class(all_pts, many=True)
#             # print(dir(Response))
#             # breakpoint()
#             # data = {'data':serializer.data, 'status':status.HTTP_200_OK, 'message':'success'}
#             # return Response(serializer.data, status=status.HTTP_200_OK)
#             # return ApiRenderer(data)
#             return create_response_util.create_response_data(
#                 message="success",
#                 status=status.HTTP_200_OK,
#                 data=serializer.data,
#                 errors=None,
#             )
#             return Response(serializer.data)
#         except Exception as e:
#             print(e)
#             data = {'data':serializer.data, 'status':status.HTTP_200_OK, 'message':'success'}
#             return Response(serializer.data)
#             # return ApiRenderer(data)
#             #
#             # return create_response_util.create_response_data(
#             #     message="failed",
#             #     status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             #     data=None,
#             #     errors=str(e),
#             # )


class PatientListForCareManagerApiView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Patient.objects.all()
    serializer_class = PatientListForCareManagerSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (PatientSearchFilter, DjangoFilterBackend,)
    filterset_class = PatientListFilter

    def get_queryset(self, *args, **kwargs):
        cm = CareManager.objects.filter(user=self.request.user.id).last()
        cm_patient = self.request.query_params.get('my_patient')
        cm_hospital_patient = self.request.query_params.get('all_patient')
        if cm_patient:
            queryset = Patient.objects.filter(
                hospital=cm.hospital, caremanager_obj=cm).order_by('-modified_at')
            return queryset
            # care_manager_hopital_branch = cm.hospital.hospital_branch.filter(care_manager=cm)
            # for hopital_branch in care_manager_hopital_branch:
            #     if hopital_branch:
            #         queryset = Patient.objects.filter(hospital=cm.hospital, caremanager_obj=cm).order_by('-modified_at')
            #         return queryset
        elif cm_hospital_patient:
            # queryset = Patient.objects.filter(hospital=cm.hospital, caremanager=None).order_by('-modified_at')
            # queryset = Patient.objects.filter(hospital=cm.hospital).exclude(
            #     caremanager_obj=cm).order_by('-modified_at')
            queryset = Patient.objects.filter(hospital=cm.hospital).order_by('-modified_at') 
            return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request):
        try:
            patients = self.filter_queryset(self.get_queryset(request))
            patients = self.paginate_queryset(patients)
            serializer = self.serializer_class(
                patients, many=True, context={"request": self.request})
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
                errors=str(e)
            )


# class PatientListForCareManagerApiView(APIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = PatientListForCareManagerSerializer
#     def get(self, request):

#         try:
#             search_type = self.request.query_params.get('type')
#             cm = CareManager.objects.filter(user=self.request.user.id).last()
#             hospital_care_manager = cm.hospital
#             patient_data = Patient.objects.filter(hospital=hospital_care_manager).all()

#             if search_type == 'patient_name':
#                 patient = self.request.query_params.get('value')
#                 term = patient.split()
#                 if len(term) > 1:
#                     patient_data = Patient.objects.filter( Q(user__first_name__icontains = term[0]) | Q(user__last_name__icontains = term[1]), hospital=hospital_care_manager)
#                 else:
#                     patient_data = Patient.objects.filter(user__first_name__icontains=patient, hospital=hospital_care_manager)

#             if search_type == "review_date":
#                 date = self.request.query_params.get('value')
#                 patient_data = Patient.objects.filter(created_at__date=date,  hospital=hospital_care_manager)

#             if search_type == 'enrolled_date':
#                 date = self.request.query_params.get('value')
#                 patient_data = Patient.objects.filter(created_at__date=date,  hospital=hospital_care_manager)

#             if search_type == 'provider_assigned':
#                 provider_assigned = self.request.query_params.get('value')
#                 patient_data = Patient.objects.filter(Q(patient_patientprovidermapping__primary_provider__user__first_name__icontains=provider_assigned) | Q(patient_patientprovidermapping__primary_provider__user__last_name__icontains=provider_assigned),  hospital=hospital_care_manager)

#             # if search_type.get('condition1'):
#             #     condition1 = self.request.query_params.get('value')
#             #     patient_data = Patient.objects.filter(condition1__icontains=condition1)

#             # if search_type.get('condition2'):
#             #     condition2 = self.request.query_params.get('value')
#             #     patient_data = Patient.objects.filter(condition2__icontains=condition2)

#             serializer = self.serializer_class(patient_data,many=True)
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
#                 errors=str(e)
#             )


class RetrieveCaremanagerPatientProfile(APIView):
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
                serializer = CaremanagerPatientProfileSerializer(patient)
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


# not required
# class CaremanagerTaskListApiView(generics.ListAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = CaremanagerTaskListSerializer
#     filter_backends = [SearchFilter]
#     search_fields = ['task__patient__user__first_name', 'created_at', 'modified_at']

#     def get_queryset(self):
#         queryset = CareManager.objects.filter(user=self.request.user).last()
#         return queryset

#     def list(self, request):
#         try:
#             cm = self.get_queryset()
#             if cm:
#                 serializer = self.serializer_class(cm)
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
#                     data=None,
#                     errors=None,
#                 )
#         except Exception as e:
#             return create_response_util.create_response_data(
#                 message="failed",
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 data=None,
#                 errors=str(e)
#             )


class PatientProviderMappingMultiplePatient(APIView):
    serializer_class = MultiplePatientSerializer

    # permission_classes = [IsAuthenticated]
    def add_multiple_user(self, data):
        for i in data['patient']:
            data = {'primary_provider': data['primary_provider'], 'patient': i}
            serializer = MultiplePatientSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
        return True

    def post(self, request):
        try:
            serializer = self.add_multiple_user(request.data)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
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


class ChronicPatientCountApiView(APIView):
    serializer_class = ChronicPatientCountSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            chronic_condition = ChronicCondition.objects.latest('disease_name')
            serializer = self.serializer_class(chronic_condition)
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


class PatientStatsTotalPatientAPIView(generics.ListAPIView):
    serializer_class = PatientStatsTotalPatientSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        try:
            cm = CareManager.objects.filter(user=request.user).last()
            patients = Patient.objects.filter(
                hospital=cm.hospital, caremanager_obj=cm)
            # care_manager_hopital_branch = cm.hospital.hospital_branch.filter(care_manager=cm)
            # patient = Patient.objects.filter(hospital=cm.hospital, caremanager__in=care_manager_hopital_branch)
            serializer = self.serializer_class(patients, many=True)
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


class PatientStatsInactivePatientAPIView(generics.ListAPIView):
    serializer_class = PatientStatsTotalPatientSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        try:
            cm = CareManager.objects.filter(user=request.user).last()
            patients = Patient.objects.filter(hospital=cm.hospital, caremanager_obj=cm,
                                              programinformation__program_type__program_name='CCM',
                                              programinformation__program_status='DECLINED')
            # care_manager_hopital_branch = cm.hospital.hospital_branch.filter(care_manager=cm)
            # ccm_declined_patient = ProgramInformation.objects.filter(program_type__program_name='CCM',program_status='DECLINED').values('patient')
            # patients = Patient.objects.filter(hospital=cm.hospital, caremanager__in=care_manager_hopital_branch, programinformation__patient__in=ccm_declined_patient).distinct()
            serializer = self.serializer_class(patients, many=True)
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


class PatientStatsNotReachablePatientAPIView(APIView):
    serializer_class = PatientStatsTotalPatientSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cm = CareManager.objects.filter(user=request.user).last()
            patients = Patient.objects.filter(hospital=cm.hospital, caremanager_obj=cm,
                                              programinformation__program_type__program_name='CCM',
                                              programinformation__program_status='NOTREACHABLE')

            # patients = Patient.objects.filter(hospital=cm.hospital, patientoutreach__resolution_action='NOT-REACHABLE', patientoutreach__contact_type='TELEPHONE-CALL', patientoutreach__care_manager=cm)

            # patients = Patient.objects.filter(hospital=cm.hospital, patientoutreach__resolution_action='NOT-REACHABLE',
            #                                   patientoutreach__contact_type='TELEPHONE-CALL', patientoutreach__care_manager=cm)

            # care_manager_hopital_branch = cm.hospital.hospital_branch.filter(care_manager=cm)
            # outreach_not_reachable_patient = PatientOutreach.objects.filter(resolution_action='NOT-REACHABLE', contact_type='PHONE').values('patient')
            # patients = Patient.objects.filter(hospital=cm.hospital, caremanager__in=care_manager_hopital_branch, patientoutreach__patient__in=outreach_not_reachable_patient).distinct()
            serializer = self.serializer_class(patients, many=True)
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


class PatientStatsEnrolledPatientAPIView(generics.ListAPIView):
    serializer_class = PatientStatsTotalPatientSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        try:
            cm = CareManager.objects.filter(user=request.user).last()
            patients = Patient.objects.filter(hospital=cm.hospital, caremanager_obj=cm,
                                              programinformation__program_type__program_name='CCM',
                                              programinformation__program_status='ACTIVE')

            # care_manager_hopital_branch = cm.hospital.hospital_branch.filter(care_manager=cm)
            # ccm_active_patient = ProgramInformation.objects.filter(program_type__program_name='CCM',program_status='ACTIVE').values('patient')
            # patients = Patient.objects.filter(hospital=cm.hospital, caremanager__in=care_manager_hopital_branch, programinformation__patient__in=ccm_active_patient).distinct()
            serializer = self.serializer_class(patients, many=True)
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


class CareManagerPatientCallLog(APIView):
    serializer_class = CareManagerPatientSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cm = CareManager.objects.filter(user=self.request.user.id).last()
            cm_patient = self.request.query_params.get('my_patient')
            cm_hospital_patient = self.request.query_params.get('all_patient')
            if cm_patient:
                patients = Patient.objects.filter(
                    hospital=cm.hospital, caremanager_obj=cm).order_by('-modified_at')
                # care_manager_hopital_branch = cm.hospital.hospital_branch.filter(care_manager=cm)
                # patients = Patient.objects.filter(hospital=cm.hospital, caremanager__in=care_manager_hopital_branch).order_by('-modified_at')
            elif cm_hospital_patient:
                patients = Patient.objects.filter(hospital=cm.hospital).exclude(
                    caremanager_obj=cm).order_by('-modified_at')
                # patients = Patient.objects.filter(hospital=cm.hospital, caremanager=None).order_by('-modified_at')

            zero_to_ten = self.request.query_params.get('0-10')
            ten_to_twenty = self.request.query_params.get('10-20')
            above_twenty = self.request.query_params.get('20')
            serializer = self.serializer_class(cm, context={"data": patients,
                                                            "zero_to_ten": zero_to_ten,
                                                            "ten_to_twenty": ten_to_twenty,
                                                            "above_twenty": above_twenty
                                                            })
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


class CaremanagerBulkUploadPatientTemplate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = {}
            data["template"] = f"{settings.BACKEND_URL}{settings.MEDIA_URL}bulk-upload-template/patient-template.xlsx"
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


class CaremanagerBulkUploadPatient(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            from tablib import Dataset
            patient_resource = PatientResource()
            dataset = Dataset()
            new_patients = request.FILES['file']
            imported_data = dataset.load(new_patients.read())
            result = patient_resource.import_data(dataset, dry_run=True)
            # return create_response_util.create_response_data(
            #     message="success",
            #     status=status.HTTP_200_OK,
            #     data=None,
            #     errors=None,
            # )
            if not result.has_errors():
                patient_resource.import_data(dataset, dry_run=False)
                return create_response_util.create_response_data(
                    message="Provider data uploded sucessfully",
                    status=status.HTTP_200_OK,
                    data=None,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="Looks like patient sheet have data which is already created.Please remove that and submit again ",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e)
            )


class CaremanagerPatientCountAPIView(APIView):
    serializer_class = CaremanagerPatientCountSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            caremanagers = CareManager.objects.all()
            serializer = self.serializer_class(caremanagers)
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


class ProviderPatientCountAPIView(APIView):
    serializer_class = ProviderPatientCountSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            providers = Provider.objects.all()
            serializer = self.serializer_class(providers)
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


class ChronicConditionPatientCountAPIView(APIView):
    serializer_class = ChronicConditionPatientCountSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            chronics = ChronicCondition.objects.all()
            serializer = self.serializer_class(chronics)
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


class CaremanagerBulkUploadProvider(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            from tablib import Dataset
            provider_resource = ProviderResource()
            dataset = Dataset()
            new_provider = request.FILES['file']
            imported_data = dataset.load(new_provider.read())
            result = provider_resource.import_data(dataset, dry_run=True)
            # return create_response_util.create_response_data(
            #     message="success",
            #     status=status.HTTP_200_OK,
            #     data=None,
            #     errors=None,
            # )
            if not result.has_errors():
                provider_resource.import_data(dataset, dry_run=False)
                return create_response_util.create_response_data(
                    message="Provider data uploded sucessfully",
                    status=status.HTTP_200_OK,
                    data=None,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="Looks like provider sheet have data which is already created.Please remove that and submit again ",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e)
            )


class CaremanagerBulkUploadProviderTemplate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = {}
            data["template"] = f"{settings.BACKEND_URL}{settings.MEDIA_URL}bulk-upload-template/provider-template.xlsx"
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


class CaremanagerTaskListApiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CaremanagerTaskOutreachListSerializer

    def get_queryset(self):
        queryset = CareManager.objects.filter(user=self.request.user).last()
        return queryset

    def list(self, request):
        try:
            cm = self.get_queryset()
            if cm:
                serializer = self.serializer_class(
                    cm, context={'request': request})
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
                errors=str(e)
            )


class GetCaremanagerHospitalView(APIView):
    serializer_class = GetCaremanagerPracticeSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cm = CareManager.objects.filter(user=self.request.user.id).last()
            # hospital_care_manager = cm.hospital
            serializer = self.serializer_class(cm)
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


class GetHospitalCareManagerApiView(APIView):
    serializer_class = GetHospitalCareManagerSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cm = CareManager.objects.filter(user=self.request.user.id).last()
            caremanagers = CareManager.objects.filter(
                hospital=cm.hospital, care_manager_status="ACTIVE")
            serializer = self.serializer_class(caremanagers, many=True)
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



@csrf_exempt
def Import_Excel_pandas(request):
        if request.method == 'POST' and request.FILES['myfile']:
            print('------------')
            myfile = request.FILES['myfile']
            
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)

            uploaded_file_url = fs.url(filename)
            
            Beneficiary_DetailsSheet = pd.read_excel(myfile, sheet_name='BeneficiaryDetails')

            InterventionSheet = pd.read_excel(myfile, sheet_name='Intervention')
            Goal_TaskSheet = pd.read_excel(myfile, sheet_name='Goal_Task')
            AllergiesSheet = pd.read_excel(myfile, sheet_name='Allergies')
            MedicationsSheet = pd.read_excel(myfile, sheet_name='Medications')
            ImmunizationSheet = pd.read_excel(myfile, sheet_name='Immunization')
            ProceduresSheet = pd.read_excel(myfile, sheet_name='Procedures')
            

            dbframe = Beneficiary_DetailsSheet
            # if Beneficiary_DetailsSheet:
                
            count_row = Beneficiary_DetailsSheet.shape[0]
            
            
            benficiary_updated_count=0
            benficiary_inserted_count=0
            for dbframe in dbframe.itertuples():
                
                
                
                try:
                    Hospital_obj = Hospital.objects.get(npi_id=dbframe.GROUP_NPI_ID)
                    
                except Hospital.DoesNotExist:  # or the generic "except ObjectDoesNotExist:"
                    Hospital_obj = Hospital(created_by=caremanager_loginobj.email, modified_by=caremanager_loginobj.email,
                                            npi_id=dbframe.GROUP_NPI_ID
                                            )
                    Hospital_obj.save()
                try:
                    caremanager_loginobj = User.objects.get(email=dbframe.SECONDARY_EMAIL)       

                    
                except User.DoesNotExist:  # or the generic "except ObjectDoesNotExist:"
                    caremanager_loginobj = User(email=dbframe.SECONDARY_EMAIL, user_type='CAREMANAGER',                                               
                                                password='welcome')
                    caremanager_loginobj.save()
                
                
               
                    
                try:
                    
                    obj = User.objects.get(email=dbframe.EMAIL)
                  
                    benficiary_updated_count=benficiary_updated_count+1
                   
                except User.DoesNotExist:  # or the generic "except ObjectDoesNotExist:"
                    
                    obj = User(email=dbframe.EMAIL, user_type='PATIENT',
                               first_name=dbframe.FIRSTNAME, last_name=dbframe.LASTNAME,
                               password='welcome',
                               created_by=caremanager_loginobj.email, modified_by=caremanager_loginobj.email)
                    obj.save()
                    benficiary_inserted_count=benficiary_inserted_count+1
                    
                try:
                    caremanager_obj = CareManager.objects.get(user__id=caremanager_loginobj.id)
                except CareManager.DoesNotExist:  # or the generic "except ObjectDoesNotExist:"
                    
                    caremanager_obj = CareManager(created_by=caremanager_loginobj.email,
                                                  modified_by=caremanager_loginobj.email, care_manager_status='Active',
                                                  secondary_email=dbframe.SECONDARY_EMAIL, hospital_id=Hospital_obj.id,
                                                  user_id=caremanager_loginobj.id
                                                  )
                    caremanager_obj.save()
                try:
                    
                   
                    objpatent_obj= Patient.objects.get(user_id=obj.id)
                    
                except Patient.DoesNotExist:
                   
                    objpatent_obj = Patient(created_by=caremanager_loginobj.email, modified_by=caremanager_loginobj.email,
                                            title=dbframe.TITLE, middle_name=dbframe.MIDDLENAME,
                                            patient_status='Active',
                                            gender=dbframe.GENDER,
                                            caremanager_obj_id=caremanager_obj.id, hospital_id=Hospital_obj.id,
                                            user_id=obj.id, )
                    objpatent_obj.save()
                
                try:
                    PatientContactDetailsr_obj = PatientContactDetails.objects.get(medicare_id=dbframe.MEDICARE_ID)
                    
                except PatientContactDetails.DoesNotExist:  # or the generic "except ObjectDoesNotExist:"
                    PatientContactDetailsr_obj = PatientContactDetails(
                                                                       medicare_id=dbframe.MEDICARE_ID,
                                                                       caremanager_id=caremanager_obj.id,
                                                                       patient_id=objpatent_obj.id,
                                                                       )
                    PatientContactDetailsr_obj.save()

            intervention = InterventionSheet
            # if InterventionSheet:
            interventioncount_row = InterventionSheet.shape[0]
            
            
            intervention_inserted_count=0
            intervention_updated_count=0
            not_inserted_count=0
            for intervention in intervention.itertuples():
                intervention_medicare=intervention.MEDICARE
                try:
                  patinetdata=PatientContactDetails.objects.get(medicare_id=intervention_medicare)
                except PatientContactDetails.DoesNotExist:
                    not_inserted_count=not_inserted_count+1
                  
                try:
                    
                    PROVIDER_EMAIl = intervention.PROVIDER_NAME.strip() + '@gmail.com'
                   
                    providerloginobj = Provider.objects.get(npi_data=intervention.Provider_NPI_ID)
                    
                    
                except Provider.DoesNotExist:  # or the generic "except ObjectDoesNotExist:"
                    providerloginobj = Provider(npi_data=intervention.Provider_NPI_ID, middle_name=intervention.PROVIDER_NAME,
                                               user_id=obj.id,hospital_id=Hospital_obj.id)
                    providerloginobj.save()
                caremanager_obj = CareManager.objects.get(secondary_email=intervention.CAREMANAGER_EMAL)
                
                contactmedicareobj = PatientContactDetails.objects.filter(patient_id=PatientContactDetailsr_obj.patient_id)
                
                objpatent_obj= Patient.objects.get(user_id=obj.id)
                
                intervention_updated_count=intervention_updated_count+1
                
                patienntoureachobj = PatientOutreach.objects.filter(patient_id=PatientContactDetailsr_obj.patient_id)
                
                
                patientoutreach_save = PatientOutreach.objects.create(patient_id=PatientContactDetailsr_obj.patient_id,contact_type=intervention.CONTACT_TYPE,
                                                                    care_manager_id=caremanager_obj.id,provider_id=providerloginobj.id, 
                                    contact_date=intervention.RECORDED_DATE,
                    resolution_action=intervention.CONTACT_RESOLUTION,
                                notes=intervention.NOTES,  created_by=caremanager_loginobj.email, modified_by=caremanager_loginobj.email)
                patientoutreach_save.save()
                intervention_inserted_count=intervention_inserted_count+1
               
            Goal_TaskSheetframe = Goal_TaskSheet
           
            gcount_row = Goal_TaskSheet.shape[0]
            goal_inserted_count=0
            #goal_updated_count=0
            goal_not_inserted_count=0
          
            for goaltask in Goal_TaskSheetframe.itertuples():
                #goal_updated_count=goal_updated_count+1
                
                if not goaltask.INTERVENTIONS=='Schedule follow-up call with patient':
                    try:
                        PatientContactDetailsr_obj = PatientContactDetails.objects.get(medicare_id=goaltask.MEDICARE)
                    except PatientContactDetails.DoesNotExist:
                            goal_not_inserted_count=goal_not_inserted_count+1
                
                    
                    goalobj=Goal.objects.create(patient_id=PatientContactDetailsr_obj.patient_id,name=goaltask.PROBLEMS,goal_status='COMPLETED',
                                            goal_date=goaltask.GOAL_START_DATE,
                                            created_by=caremanager_loginobj.email,
                                                                    modified_by=caremanager_loginobj.email)
                    goalobj.save()
                    goal_inserted_count=goal_inserted_count+1
                if  goaltask.INTERVENTIONS=='Schedule follow-up call with patient':
                    count=0
                    pdcount=0
                    try:
                        
                        try:
                            PatientContactDetailsr_obj = PatientContactDetails.objects.get(medicare_id=goaltask.MEDICARE)
                            goal=Goal.objects.filter(patient_id=PatientContactDetailsr_obj.patient_id).last()
                            
                            
                            
                            PatientContactDetailsr_obj = PatientContactDetails.objects.get (medicare_id=goaltask.MEDICARE)
                        except PatientContactDetails.DoesNotExist :
                            #goal_not_inserted_count=goal_not_inserted_count
                            pdcount= pdcount+1
                            
                            
                        
                        if goal.patient_id == PatientContactDetailsr_obj.patient_id:
                            
                            taskobj=Task.objects.create(patient_id=PatientContactDetailsr_obj.patient_id,goal_id=goal.id,name=goaltask.INTERVENTIONS,task_status='PENDING',
                                                    
                                                    created_by=caremanager_loginobj.email,
                                                                            modified_by=caremanager_loginobj.email)
                            taskobj.save()
                    except AttributeError :
                        goalmedicare=goaltask.MEDICARE
                        
                        count=count+1
                        
            allergiesframe = AllergiesSheet
               
            alergycount_row = AllergiesSheet.shape[0]
            allergy_inserted_count=0
            allergy_updated_count=0
            allergy_not_inserted_count=0
            
            for allergie in allergiesframe.itertuples():
                allergie_medicare=allergie.MEDICARE_ID
                try:
                  PatientContactDetailsr_obj = PatientContactDetails.objects.get(medicare_id=allergie.MEDICARE_ID)
                except PatientContactDetails.DoesNotExist:
                    allergy_not_inserted_count=allergy_not_inserted_count+1
                
                allergieobj = Allergies.objects.create(patient_id=PatientContactDetailsr_obj.patient_id,
                                     name=allergie.ALLERGY_NAME, 
                                     description=allergie.allergie_desc,
                                      source_entry=allergie.source_entry,
                                     
                                     created_by=caremanager_loginobj.email,
                                     modified_by=caremanager_loginobj.email)
                allergieobj.save()
                allergy_inserted_count=allergy_inserted_count+1


            medicationframe = MedicationsSheet
            
            
                
            medicationcount_row = MedicationsSheet.shape[0]
            medication_inserted_count=0
            medication_updated_count=0
            medication_not_inserted=0
            

            for medication in medicationframe.itertuples():
                #medication_updated_count=medication_updated_count+1
                try:
                  PatientContactDetailsr_obj = PatientContactDetails.objects.get(medicare_id=medication.MEDICARE_ID)
                except PatientContactDetails.DoesNotExist:
                    medication_not_inserted=medication_not_inserted+1

                # contactmedicareobj = PatientContactDetails.objects.get(medicare_id=medication.MEDICARE_ID)
                
                # PatientContactDetailsr_obj = PatientContactDetails.objects.get(medicare_id=medication.MEDICARE_ID)
               
                # medicationpatientobj = Intervention.objects.filter(patient_id=PatientContactDetailsr_obj.patient_id)
                
                medicationobj = Medication.objects.create(patient_id=PatientContactDetailsr_obj.patient_id,
                                     medication_name=medication.DRUGNAME,
                                     dose=medication.DOSE,
                                     prescriber=medication.PRESCRIBER_NAME,
                                     midication_status=medication.STATUS,
                                     frequency=medication.FREQUENCY,
                                     created_by=caremanager_loginobj.email,
                                     modified_by=caremanager_loginobj.email)
                medicationobj.save()
                medication_inserted_count=medication_inserted_count+1

            imunizationframe = ImmunizationSheet
           
                
            immunizationcount_row = ImmunizationSheet.shape[0]
            immunization_inserted_count=0
            immunization_updated_count=0
            immunization_not_inserted_count=0
            

            for immunization in imunizationframe.itertuples():
                    #immunization_updated_count=immunization_updated_count+1
                    try:
                        PatientContactDetailsr_obj = PatientContactDetails.objects.get(medicare_id=immunization.MEDICARE_ID)
                    except PatientContactDetails.DoesNotExist:
                            immunization_not_inserted_count=immunization_not_inserted_count+1

                    # contactmedicareobj = PatientContactDetails.objects.get(medicare_id=immunization.MEDICARE_ID)
                    
                
                    # PatientContactDetailsr_obj = PatientContactDetails.objects.get(medicare_id=immunization.MEDICARE_ID)
                    
                    # procedurepatientobj = Immunization.objects.filter(patient_id=PatientContactDetailsr_obj.patient_id)
                    
                
                    
                    immuniazationobj = Immunization.objects.create(patient_id=PatientContactDetailsr_obj.patient_id,
                                       name=immunization.SOURCE_ENTRY,
                                       description=immunization.IMMUNIZATION_DESC,
                                       created_by=caremanager_loginobj.email,
                                       source_entry=immunization.SOURCE_ENTRY,
                                       modified_by=caremanager_loginobj.email)
                    immuniazationobj.save()
                    immunization_inserted_count=immunization_inserted_count+1
                    
                    

            procedureframe = ProceduresSheet
            
                
            procedurecount_row = ProceduresSheet.shape[0]
            procedure_inserted_count=0
            procedure_updated_count=0
            procedure_not_inserted_count=0
            
            for procedure in procedureframe.itertuples():
                #procedure_updated_count=procedure_updated_count+1
                try:
                        PatientContactDetailsr_obj = PatientContactDetails.objects.get(medicare_id=procedure.MEDICARE_ID)
                except PatientContactDetails.DoesNotExist:
                            procedure_not_inserted_count=procedure_not_inserted_count+1

                # contactmedicareobj = PatientContactDetails.objects.get(medicare_id=procedure.MEDICARE_ID)
                # PatientContactDetailsr_obj = PatientContactDetails.objects.get(medicare_id=procedure.MEDICARE_ID)
                # procedurepatientobj = Procedures.objects.filter(patient_id=PatientContactDetailsr_obj.patient_id)
                
                
                procedureobj = Procedures.objects.create(patient_id=PatientContactDetailsr_obj.patient_id,
                                       name=procedure.SOURCE_ENTRY,
                                       description=procedure.PROCEDURE_DESC,
                                       created_by=caremanager_loginobj.email,
                                       modified_by=caremanager_loginobj.email)
                procedureobj.save()
                procedure_inserted_count=procedure_inserted_count+1
            data = {
            'message':'file uploaded successfully',
            'uploaded_file_url': uploaded_file_url,
            'beneficiary_total count':count_row,
            'bbeneficiary_inserted_count':benficiary_inserted_count,
            'beneficiary_updated_count':benficiary_updated_count,
            'intervention_total_count':interventioncount_row,
            'intervention_inserted_count':intervention_inserted_count,
            'intervention_not_inserted_count':not_inserted_count,
            'allergies_total_count':alergycount_row,
            'allergies_inserted_count':allergy_inserted_count,
            'allergies_not_inserted_count':allergy_not_inserted_count,
            'procedures_total_count':procedurecount_row,
            'procedures_inserted_count':procedure_inserted_count,
            'procedures_not_inserted_count':procedure_not_inserted_count,
            'goal_total_count':gcount_row,
            'goal_inserted_count':goal_inserted_count,
            'goal_not_inserted_count':count+pdcount,
            'medications_total_count':medicationcount_row,
            'medications_inserted_count':medication_inserted_count,
            'medications_not_inserted':medication_not_inserted,
            'immunization_total_count':immunizationcount_row,
            'immunization_inserted_count':immunization_inserted_count,
            'immunization_not_inserted_count':immunization_not_inserted_count,
              }
            return JsonResponse(data=data)








        #return render(request, 'import_excel_db.html', {'uploaded_file_url': ""})



class CareManagerDuration(APIView):

    #import datetime
    def get(self, request, caremanager_id, year,format=None):
            list = []
            today = datetime.now()
            month = today.strftime("%m")
           
              
            month_name = today.strftime("%b")
            
            start_date='2023-01-01'
            end_date=date.today()
           



            toatl_patient1 = Patient.objects.filter( created_at__month=month,caremanager_obj_id=caremanager_id)
            toatl_patient01 = Patient.objects.filter( created_at__month='01',caremanager_obj_id=caremanager_id)
            toatl_patient2 = Patient.objects.filter( created_at__month='02',caremanager_obj_id=caremanager_id)
            toatl_patient3 = Patient.objects.filter( created_at__month='03',caremanager_obj_id=caremanager_id)
            toatl_patient4 = Patient.objects.filter( created_at__month='04',caremanager_obj_id=caremanager_id)

            toatl_patient5 = Patient.objects.filter(created_at__month='05',caremanager_obj_id=caremanager_id)
            toatl_patient6 = Patient.objects.filter( created_at__month='06',caremanager_obj_id=caremanager_id)
            toatl_patient7 = Patient.objects.filter( created_at__month='07',caremanager_obj_id=caremanager_id)

            toatl_patient8 = Patient.objects.filter( created_at__month='08',caremanager_obj_id=caremanager_id)
            toatl_patient9 = Patient.objects.filter( created_at__month='09',caremanager_obj_id=caremanager_id)
            toatl_patient10 = Patient.objects.filter( created_at__month='10',caremanager_obj_id=caremanager_id)
            toatl_patient11 = Patient.objects.filter( created_at__month='11',caremanager_obj_id=caremanager_id)

            toatl_patient12 = Patient.objects.filter( created_at__month='12',caremanager_obj_id=caremanager_id)



            enrolled_patients1 =ProgramInformation.objects.filter(
                      date__month=month, program_type_id='1',program_status='ACTIVE',)
            # enrolled_patients1 =ProgramInformation.objects.filter(date__year='2023', 
            #           date__month='01', program_type_id='1',program_status='ACTIVE',)
            enrolled_patients01 =ProgramInformation.objects.filter(
                      date__month='01', program_type_id='1',program_status='ACTIVE',)
           
            enrolled_patients2 =ProgramInformation.objects.filter(
                      date__month='02', program_type_id='1',program_status='ACTIVE',)
            enrolled_patients3 =ProgramInformation.objects.filter(
                      date__month='03', program_type_id='1',program_status='ACTIVE',)
            enrolled_patients4 =ProgramInformation.objects.filter(
                      date__month='04', program_type_id='1',program_status='ACTIVE',)
            enrolled_patients5 =ProgramInformation.objects.filter(
                      date__month='05', program_type_id='1',program_status='ACTIVE',)
            enrolled_patients6 =ProgramInformation.objects.filter(
                      date__month='06', program_type_id='1',program_status='ACTIVE',)
            enrolled_patients7 =ProgramInformation.objects.filter(
                      date__month='07', program_type_id='1',program_status='ACTIVE',)
            enrolled_patients8 =ProgramInformation.objects.filter(
                      date__month='08', program_type_id='1',program_status='ACTIVE',)
            enrolled_patients9 =ProgramInformation.objects.filter(
                      date__month='09', program_type_id='1',program_status='ACTIVE',)
            enrolled_patients10 =ProgramInformation.objects.filter(
                      date__month='10', program_type_id='1',program_status='ACTIVE',)
            enrolled_patients11 =ProgramInformation.objects.filter(
                      date__month='11', program_type_id='1',program_status='ACTIVE',)
            enrolled_patients12 =ProgramInformation.objects.filter(
                      date__month='12', program_type_id='1',program_status='ACTIVE',)

            inactive_patients1 =ProgramInformation.objects.filter(
                      date__month=month, program_type_id='1',program_status='INACTIVE')

            inactive_patients12 =ProgramInformation.objects.filter(
                      date__month='12', program_type_id='1',program_status='INACTIVE')
            inactive_patients11 =ProgramInformation.objects.filter(
                      date__month='11', program_type_id='1',program_status='INACTIVE')
            inactive_patients10 =ProgramInformation.objects.filter(
                      date__month='10', program_type_id='1',program_status='INACTIVE')
            inactive_patients9 =ProgramInformation.objects.filter(
                      date__month='09', program_type_id='1',program_status='INACTIVE')
            inactive_patients8 =ProgramInformation.objects.filter(
                      date__month='08', program_type_id='1',program_status='INACTIVE')
            inactive_patients7 =ProgramInformation.objects.filter(
                      date__month='07', program_type_id='1',program_status='INACTIVE')
            inactive_patients6 =ProgramInformation.objects.filter(
                      date__month='06', program_type_id='1',program_status='INACTIVE')
            inactive_patients5 =ProgramInformation.objects.filter(
                      date__month='05', program_type_id='1',program_status='INACTIVE')
            inactive_patients4 =ProgramInformation.objects.filter(
                      date__month='04', program_type_id='1',program_status='INACTIVE')
            inactive_patients3 =ProgramInformation.objects.filter(
                      date__month='03', program_type_id='1',program_status='INACTIVE')
            inactive_patients2 =ProgramInformation.objects.filter(
                      date__month='02', program_type_id='1',program_status='INACTIVE')
            inactive_patients01 =ProgramInformation.objects.filter(
                      date__month='01', program_type_id='1',program_status='INACTIVE')

            not_reachable1 =PatientOutreach.objects.filter( 
                      date__month=month, notes='Not Reachable',contact_type='Telephone Call',care_manager_id=caremanager_id)
            not_reachable01 =PatientOutreach.objects.filter( 
                      date__month='01', notes='Not Reachable',contact_type='Telephone Call',care_manager_id=caremanager_id)
            
            not_reachable2 =PatientOutreach.objects.filter( 
                      date__month='02', notes='Not Reachable',contact_type='Telephone Call',care_manager_id=caremanager_id)
            not_reachable3 =PatientOutreach.objects.filter( 
                      date__month='03', notes='Not Reachable',contact_type='Telephone Call',care_manager_id=caremanager_id)
            not_reachable4 =PatientOutreach.objects.filter(
                      date__month='04', notes='Not Reachable',contact_type='Telephone Call',care_manager_id=caremanager_id)
            not_reachable5 =PatientOutreach.objects.filter(
            date__month='05', notes='Not Reachable',contact_type='Telephone Call',care_manager_id=caremanager_id)
            not_reachable6 =PatientOutreach.objects.filter(
            date__month='06', notes='Not Reachable',contact_type='Telephone Call',care_manager_id=caremanager_id)
            not_reachable7 =PatientOutreach.objects.filter(
            date__month='07', notes='Not Reachable',contact_type='Telephone Call',care_manager_id=caremanager_id)
            not_reachable8 =PatientOutreach.objects.filter(
            date__month='08', notes='Not Reachable',contact_type='Telephone Call',care_manager_id=caremanager_id)
            not_reachable9 =PatientOutreach.objects.filter(
            date__month='09', notes='Not Reachable',contact_type='Telephone Call',care_manager_id=caremanager_id)
            not_reachable10 =PatientOutreach.objects.filter(
            date__month='10', notes='Not Reachable',contact_type='Telephone Call',care_manager_id=caremanager_id)
            not_reachable11 =PatientOutreach.objects.filter(
            date__month='11', notes='Not Reachable',contact_type='Telephone Call',care_manager_id=caremanager_id)
            not_reachable12 =PatientOutreach.objects.filter(
            date__month='12', notes='Not Reachable',contact_type='Telephone Call',care_manager_id=caremanager_id)

            callduration1 = PatientOutreach.objects.filter(date__month=month,time_spent__gt='0:20:00',care_manager_id=caremanager_id)
            callduration01 = PatientOutreach.objects.filter(date__month='02',time_spent__gt='0:20:00',care_manager_id=caremanager_id)
            callduration2 = PatientOutreach.objects.filter(date__month='02',time_spent__gt='0:20:00',care_manager_id=caremanager_id)
            callduration3 = PatientOutreach.objects.filter(date__month='03',time_spent__gt='0:20:00',care_manager_id=caremanager_id)
            callduration4 = PatientOutreach.objects.filter(date__year='2023',date__month='04',time_spent__gt='00:20',care_manager_id=caremanager_id)
            callduration5 = PatientOutreach.objects.filter(date__year='2023',date__month='05',time_spent__gt='00:20',care_manager_id=caremanager_id)
            callduration6 = PatientOutreach.objects.filter(date__year='2023',date__month='06',time_spent__gt='00:20',care_manager_id=caremanager_id)
            callduration7 = PatientOutreach.objects.filter(date__month='07',time_spent__gt='00:20',care_manager_id=caremanager_id)
            callduration8 = PatientOutreach.objects.filter(date__month='08',time_spent__gt='00:20',care_manager_id=caremanager_id)
            callduration9 = PatientOutreach.objects.filter(date__month='09',time_spent__gt='00:20',care_manager_id=caremanager_id)
            callduration10 = PatientOutreach.objects.filter(date__month='10',time_spent__gt='00:20',care_manager_id=caremanager_id)
            callduration11 = PatientOutreach.objects.filter(date__month='11',time_spent__gt='00:20',care_manager_id=caremanager_id)
            callduration12 = PatientOutreach.objects.filter(date__month='12',time_spent__gt='00:20',care_manager_id=caremanager_id)


            toatl_patientbyyear = Patient.objects.filter(created_at__year=year,caremanager_obj_id=caremanager_id)

            enrolled_patientsbyyear =ProgramInformation.objects.filter(date__year=year, 
                    program_type_id='1', program_status='ACTIVE',)
            print('enrolled_patientsbyyear=', enrolled_patientsbyyear.count())
            inactive_patientsbyyear =ProgramInformation.objects.filter(date__year=year, 
                     program_type_id='1', program_status='INACTIVE')
            not_reachablebyyear =PatientOutreach.objects.filter(date__year=year, 
                      notes='Not Reachable', contact_type='Telephone Call',care_manager_id=caremanager_id)
            calldurationbyyear = PatientOutreach.objects.filter(time_spent__gt='0:20:00',care_manager_id=caremanager_id)
            
            
           

            for current_month in range(1,int(month)+int(1)):
                            toatl_patient=Patient.objects.filter(created_at__month=current_month,caremanager_obj_id=caremanager_id)
                            
                            enrolled_patients=ProgramInformation.objects.filter(date__month = current_month,program_type_id='1',program_status='ACTIVE',)
                            

                            inactive_patients=ProgramInformation.objects.filter(date__month = current_month,program_type_id='1',program_status='INACTIVE')
                           
                            not_reachable=PatientOutreach.objects.filter(date__month = current_month,notes='Not Reachable',contact_type='Telephone Call',care_manager_id=caremanager_id)
                          
                            callduration=PatientOutreach.objects.filter(date__month=current_month,time_spent__gt='0:20:00',care_manager_id=caremanager_id)

                            data={

                                    current_month: {
                                        'toatl_patients':toatl_patient.count(),
                                    'total_enrolled_patients': enrolled_patients.count(),
                                    'total_inactive_patients': inactive_patients.count(),
                                    'total_not_reachable_patients': not_reachable.count(),
                                    'over_20_minutes':callduration.count()
                                    }
                                }
                            print('data=',data)
                            list.append(data)
            
            
            

            data ={
                'monthly':{
                    
                    month_name: {
                                 'total_patients': toatl_patient1.count(),
                    'total_enrolled_patients': enrolled_patients1.count(),
                    'total_inactive_patients': inactive_patients1.count(),
                    'total_not_reachable_patients': not_reachable1.count(),
                    'over_20_minutes': callduration1.count()

                                 },
                    },
                'Yearly': {
                        'total_patients': toatl_patientbyyear.count(),
                        'total_enrolled_patients': enrolled_patientsbyyear.count(),
                        'total_inactive_patients': inactive_patientsbyyear.count(),
                        'total_total_not_reachable_patients': not_reachablebyyear.count(),
                        'over_20_minutes': calldurationbyyear.count()


                    },
                
                    
                    
                'Quarterly':{
                        "Q1":
                            {
                                 'Jan': {
                                 'total_patient': toatl_patient01.count(),
                   'enrolled_patients': enrolled_patients01.count() ,
                   'total_inactive_patients': inactive_patients01.count(),
                    'total_not_reachable_patients': not_reachable01.count(),
                    'over_20_minutes': callduration01.count()
                                 },
                                
                                
                            'Feb': {
                                 'total_patient': toatl_patient2.count(),
                   'total_enrolled_patients': enrolled_patients2.count() ,
                   'total_inactive_patients': inactive_patients2.count(),
                    'total_not_reachable_patients': not_reachable2.count(),
                    'over_20_minutes': callduration2.count()
                                 },
                                          'Mar': {
                                              'total_patient': toatl_patient3.count(),
                   'total_enrolled_patients': enrolled_patients3.count() 
                                 ,
                   'total_inactive_patients': inactive_patients3.count(),
                    'total_not_reachable_patients': not_reachable3.count(),
                    'over_20_minutes': callduration3.count()
                                          }
                                
                                
                                
                            },
                     "Q2":{
                          'Apr': {
                                    'total_patient': toatl_patient4.count(),
                   'total_enrolled_patients': enrolled_patients4.count() 
                                 ,
                   'total_inactive_patients': inactive_patients4.count(),
                   'total_not_reachable_patients': not_reachable4.count(),
                    'over_20_minutes': callduration4.count()
                                 },
                                            'May': {
                                                'total_patient': toatl_patient5.count(),
                   'total_enrolled_patients': enrolled_patients5.count() 
                                 ,
                   'total_inactive_patients': inactive_patients5.count(),'total_not_reachable_patients':not_reachable5.count(),
                    'over_20_minutes': callduration5.count()
                                 },

                               'Jun': {
                                   'total_patient': toatl_patient6.count(),
                   'total_enrolled_patients': enrolled_patients6.count()
                                 ,
                   'total_inactive_patients': inactive_patients6.count(), 'total_not_reachable_patients':not_reachable6.count(),
                    'over_20_minutes': callduration6.count()
                                 },
                     },
                     "Q3":{
                          'Jul': {
                                  'total_patient': toatl_patient7.count(),
                   'total_enrolled_patients': enrolled_patients7.count() 
                                 ,
                   'total_inactive_patients': inactive_patients7.count(),'total_not_reachable_patients':not_reachable7.count(),
                    'over_20_minutes': callduration7.count()
                                 },
                                         'Aug': {
                                             'total_patient': toatl_patient8.count(),
                   'total_enrolled_patients': enrolled_patients8.count() 
                                 ,
                   'total_inactive_patients': inactive_patients8.count(),'total_not_reachable_patients':not_reachable8.count(),
                    'over_20_minutes': callduration8.count()
                                 },
                                                     'Sep': {
                                                         'total_patient': toatl_patient9.count(),
                   'total_enrolled_patients': enrolled_patients9.count() 
                                 ,
                   'total_inactive_patients': inactive_patients9.count(),'total_not_reachable_patients':not_reachable9.count(),
                    'over_20_minutes': callduration9.count()
                                 },
                         
                     },
                      "Q4":{
                            'Oct': {
                              'total_patient': toatl_patient10.count(),
                   'total_enrolled_patients': enrolled_patients10.count() 
                                 ,
                   'total_inactive_patients': inactive_patients10.count(),'total_not_reachable_patients':not_reachable10.count(),
                    'over_20_minutes': callduration10.count()
                                 },
                          'Nov': {
                              'total_patient': toatl_patient11.count(),
                   'total_enrolled_patients': enrolled_patients11.count() ,
                   'total_inactive_patients': inactive_patients11.count(),'total_not_reachable_patients':not_reachable11.count(),
                    'over_20_minutes': callduration11.count()
                                 },
                              'Dec': {
                                  'total_patient':toatl_patient12.count(),
                   'total_enrolled_patients': enrolled_patients12.count() ,
                   'total_inactive_patients': inactive_patients12.count(),'total_not_reachable_patients':not_reachable12.count(),
                    'over_20_minutes': callduration12.count()
                                     },
                      },
                    },
                                 
                        
                    'Bi-Annual':{
                        '1':{
                            'Jan': {
                                 'total_patient': toatl_patient01.count(),
                   'total_enrolled_patients': enrolled_patients01.count() ,
                   'total_inactive_patients': inactive_patients01.count(),
                    'total_not_reachable_patients': not_reachable01.count(),
                    'over_20_minutes': callduration01.count()
                                 },
                                
                                
                            'Feb': {
                                 'total_patient': toatl_patient2.count(),
                   'total_enrolled_patients': enrolled_patients2.count() ,
                   'total_inactive_patients': inactive_patients2.count(),
                    'total_not_reachable_patients': not_reachable2.count(),
                    'over_20_minutes': callduration2.count()
                                 },
                                          'Mar': {
                                              'total_patient': toatl_patient3.count(),
                   'total_enrolled_patients': enrolled_patients3.count() 
                                 ,
                   'total_inactive_patients': inactive_patients3.count(),
                    'total_not_reachable_patients': not_reachable3.count(),
                    'over_20_minutes': callduration3.count()
                                          },
                                            'Apr': {
                                    'total_patient': toatl_patient4.count(),
                   'total_enrolled_patients': enrolled_patients4.count() 
                                 ,
                   'total_inactive_patients': inactive_patients4.count(),
                   'total_not_reachable_patients': not_reachable4.count(),
                    'over_20_minutes': callduration4.count()
                                 },
                                            'May': {
                                                'total_patient': toatl_patient5.count(),
                   'total_enrolled_patients': enrolled_patients5.count() 
                                 ,
                   'total_inactive_patients': inactive_patients5.count(),'total_not_reachable_patients':not_reachable5.count(),
                    'over_20_minutes': callduration5.count()
                                 },

                               'Jun': {
                                   'total_patient': toatl_patient6.count(),
                   'total_enrolled_patients': enrolled_patients6.count()
                                 ,
                   'total_inactive_patients': inactive_patients6.count(), 'total_not_reachable_patients':not_reachable6.count(),
                    'over_20_minutes': callduration6.count()
                                 },
                                
                    },
                    '2':{
                            'Jul': {
                                  'total_patient': toatl_patient7.count(),
                   'total_enrolled_patients': enrolled_patients7.count() 
                                 ,
                   'total_inactive_patients': inactive_patients7.count(),'total_not_reachable_patients':not_reachable7.count(),
                    'over_20_minutes': callduration7.count()
                                 },
                                         'Aug': {
                                             'total_patient': toatl_patient8.count(),
                   'total_enrolled_patients': enrolled_patients8.count() 
                                 ,
                   'total_inactive_patients': inactive_patients8.count(),'total_not_reachable_patients':not_reachable8.count(),
                    'over_20_minutes': callduration8.count()
                                 },
                                                     'Sep': {
                                                         'total_patient': toatl_patient9.count(),
                   'total_enrolled_patients': enrolled_patients9.count() 
                                 ,
                   'total_inactive_patients': inactive_patients9.count(),'total_not_reachable_patients':not_reachable9.count(),
                    'over_20_minutes': callduration9.count()
                                 },
                                                      'Oct': {
                              'total_patient': toatl_patient10.count(),
                   'total_enrolled_patients': enrolled_patients10.count() 
                                 ,
                   'total_inactive_patients': inactive_patients10.count(),'total_not_reachable_patients':not_reachable10.count(),
                    'over_20_minutes': callduration10.count()
                                 },
                          'Nov': {
                              'total_patient': toatl_patient11.count(),
                   'total_enrolled_patients': enrolled_patients11.count() ,
                   'total_inactive_patients': inactive_patients11.count(),'total_not_reachable_patients':not_reachable11.count(),
                    'over_20_minutes': callduration11.count()
                                 },
                              'Dec': {
                                  'total_patient':toatl_patient12.count(),
                   'total_enrolled_patients': enrolled_patients12.count() ,
                   'total_inactive_patients': inactive_patients12.count(),'total_not_reachable_patients':not_reachable12.count(),
                    'over_20_minutes': callduration12.count()
                                     },
                        },
                    
                    'YTD':list


            },
            }
            #print('data=', data)
            
            return Response(data)

            # for current_month in range(1,13):
            #                 toatl_patient=Patient.objects.filter(created_at__month=current_month,caremanager_obj_id=caremanager_id)
            #                 print('toatl_patient=',toatl_patient.count())
            #                 enrolled_patients=ProgramInformation.objects.filter(date__month = current_month,program_type_id='1',program_status='ACTIVE',)
            #                 #print('enrolled_patients ' +str(current_month),enrolled_patients.count())

            #                 inactive_patients=ProgramInformation.objects.filter(date__month = current_month,program_type_id='1',program_status='INACTIVE')
            #                 #print('inactive_patients=',inactive_patients.count())
            #                 not_reachable=PatientOutreach.objects.filter(date__month = current_month,notes='Not Reachable',contact_type='Telephone Call',care_manager_id=caremanager_id)
            #                 #print('not_reachable=',not_reachable.count())
            #                 callduration=PatientOutreach.objects.filter(date__month=current_month,time_spent__gt='00:20',care_manager_id=caremanager_id)

            #                 data={

            #                         current_month: {
            #                             'toatl_patient':toatl_patient.count(),
            #                         'total_enrolled_patients': enrolled_patients.count(),
            #                         'total_inactive_patients': inactive_patients.count(),
            #                         'total_not_reachable': not_reachable.count(),
            #                         'over_20_minutes':callduration.count()
            #                         }
            #                     }
            #                 print('data=',data)
            #                 list.append(data)
            # print('list=',list)

            # return Response(data=list)







class GetCareManagerlistApiView(generics.ListAPIView):
    pagination_class = PageNumberPagination
    serializer_class = GetCareManagerlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        search = self.request.query_params.get('search')
        cm = CareManager.objects.filter(user=self.request.user.id).last()
        if search:
            queryset = CareManager.objects.annotate(
                full_name=Concat('user__first_name', Value(' '), 'user__last_name')
            ).filter(Q(contact__icontains=search) |
                     Q(user__email__icontains=search) |
                     Q(full_name__icontains=search),
                     hospital=cm.hospital,
                     care_manager_status="ACTIVE")
        else:
            queryset = CareManager.objects.filter(
                hospital=cm.hospital, care_manager_status="ACTIVE")
        return queryset

    def list(self, request):
        try:
            cm = self.filter_queryset(self.get_queryset(request)).order_by('-created_at')
            data = self.paginate_queryset(cm)
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


class GetCareManagerListSortByMinutesApiView(APIView):
    pagination_class = PageNumberPagination
    serializer_class = GetCareManagerListSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cm = CareManager.objects.filter(user=self.request.user.id).last()
            # caremanagers = CareManager.objects.filter()
            # cm_hospital_patient = self.request.query_params.get('sort_by_minute')
            # data = self.paginate_queryset(cm)
            zero_to_ten = self.request.query_params.get('0-10')
            ten_to_twenty = self.request.query_params.get('10-20')
            above_twenty = self.request.query_params.get('20')
            serializer = self.serializer_class(cm, context={"zero_to_ten": zero_to_ten,
                                                            "ten_to_twenty": ten_to_twenty,
                                                            "above_twenty": above_twenty
                                                            })
            # serializer = self.serializer_class(data, many=True)
            # pages = self.paginate_queryset(serializer.data)
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


class AssignPatientListView(generics.ListAPIView):
    serializer_class = AssignPatientListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        cm = CareManager.objects.filter(user=self.request.user.id).last()
        hospital_care_manager = cm.hospital
        queryset = Provider.objects.filter(hospital=hospital_care_manager, id=self.kwargs["provider_id"]).exclude(
            provider_status="SUSPENDED").order_by("-modified_at")
        return queryset

    def list(self, request, provider_id):
        try:
            provider = self.get_queryset(id=provider_id)
            serializer = self.serializer_class(provider, many=True)
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





            
class CareManagerCompletedMins(APIView):
    
    def get(self,request,care_manager_id):
        zerototenmins=PatientCallLog.objects.all()
        caremanger=CareManager.objects.all()
        serializers=MultiSerializers((zerototenmins,caremanger),many=True)
        print('serializers=',serializers)
        return Response(data=serializers.data)
        
        
        
        # start_range='00:00:00'
        # endrange='00:10:00'
        # start_range2='00:11:00'
        # endrange2='00:19:00'
        # start_range3='00:20:00'
        # endrange3='00:29:00'
        # start_range1='00:30:00'
        # endrange1='00:39:20'
        # start_range4='00:40:00'
        # zerototenmins=PatientCallLog.objects.filter(care_manager_id=care_manager_id,call_duration__range=[start_range,endrange])
        # print('zerototenmins=',zerototenmins)
        # zerototenmins1=PatientCallLog.objects.filter(care_manager_id=care_manager_id,call_duration__range=[start_range1,endrange1])
        # print('zerototenmins1=',zerototenmins1)
        # zerototenmins2=PatientCallLog.objects.filter(care_manager_id=care_manager_id,call_duration__range=[start_range2,endrange2])
        # zerototenmins3=PatientCallLog.objects.filter(care_manager_id=care_manager_id,call_duration__range=[start_range3,endrange3])
        # zerototenmins4=PatientCallLog.objects.filter(care_manager_id=care_manager_id,call_duration__gte=start_range4)
        # data={
        #     'data':{
                
        #         'Zero_to_ten_(0-10)':zerototenmins.count(),
        #         'Eleven_to_Nineteen_(11-19)':zerototenmins2.count(),
        #         'Twenty_to_twentynine_(20-29)':zerototenmins3.count(),
        #         'Thirty_to_thirtynine_(30-39)':zerototenmins1.count(),
        #          'Morethen_40_Mins_(40+)':zerototenmins4.count()
        #     },
        #     'message':'success',
        #     'status':status.HTTP_200_OK,
            
        #     }
        
           
        return Response( data=data)
    
    
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper
import mimetypes
    
class Export_execl(APIView):
    def get(self,request):
        base_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filename='CCM-Export-wcandi.xlsx'
        print('filename=',filename)
        filepath =base_dir+'/Files/'+filename
        print('filepath=',filepath)
        thefile=filepath
        filename=os.path.basename(thefile)
        chunk_size=8192
        response=StreamingHttpResponse(FileWrapper(open(thefile, 'rb'),chunk_size),
        content_type=mimetypes.guess_type(thefile)[0])
        response['Content-Length']=os.path.getsize(thefile)
        response['Content-Disposition']="Attachment;filename=%s"%filename
       
        return response
    
    
    
              



