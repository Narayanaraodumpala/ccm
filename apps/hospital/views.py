import datetime
import pandas as pd
from collections import Counter

from django.db.models import Q, OuterRef, Subquery
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status, generics
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response

from apps.authentication.models import User
from apps.account_manager import create_response_util
from apps.account_manager.models import Patient, Provider, CareManager, PracticeAdmin

from apps.hospital.models import (
    Appointment,
    Hospital,
    HospitalBranch,
    Medication,
    MedicationChronicCondition,
    Treatment,
    Department,
    ChronicCondition,
    NPI,
    PatientChronicDisease,
    NPITaxonomy,
)
from apps.hospital.serializers import (
    AppointmentSerializer,
    HospitalSerializer,
    HospitalBranchSerializer,
    MedicationSerializer,
    PatientMedicationChronicDiseaseListSerializer,
    TreatmentSerializer,
    DepartmentSerializer,
    CronicConditionSerializer,
    HospitaldataListSerializer,
    HospitalRelatedUserSerializer,
    HospitalPutSerializer,
    HospitalBranchLocationSerializer,
    HospitalTestSerializer,
    PatientChronicDiseaseSerializer,
    AssignChronicConditionSerializer,
    ChronicConditionSerializer,
    PatientChronicDiseaseCreateSerializer,
    PatientChronicDiseaseListSerializer,
    PatientChronicDiseaseUpdateSerializer,
    NPITaxonomySerializer,
    MedicationListSerializer,
)

from apps.account_manager.utils import HospitalFilter
from apps.account_manager.create_response_util import ApiRenderer
from apps.hospital.utils import ChronicDiseaseFilter, MedicationFilter, FilterMdeication
from apps.patient.utils import CustomPageNumberPagination


class AppointmentView(APIView):
    """
    List all appointments, or create a new appointment.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            appointments = Appointment.objects.all()
            serializer = AppointmentSerializer(appointments, many=True)
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
            serializer = AppointmentSerializer(data=request.data)
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
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class AppointmentDetailView(APIView):
    """
    Retrieve, update or delete a appointment instance.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            data = Appointment.objects.get(pk=pk)
            return data
        except Appointment.DoesNotExist:
            return None

    def get(self, request, pk):
        try:
            appointment = self.get_object(pk)
            if appointment is not None:
                serializer = AppointmentSerializer(appointment)
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

    def put(self, request, pk):
        try:
            appointment = self.get_object(pk)
            if appointment is not None:
                serializer = AppointmentSerializer(appointment, data=request.data)
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

    def delete(self, request, pk):
        try:
            appointment = self.get_object(pk)
            if appointment is not None:
                appointment.delete()
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


# Hospital
class HospitalView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HospitalSerializer
    pagination_class = CustomPageNumberPagination
    queryset = Hospital.objects.all()
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = HospitalFilter
    search_fields = ["id", "hospital_name", "npi_id", "address_1"]

    """
    List all hospitals, or create a new hospitals.
    """

    def get_queryset(self, *args, **kwargs):
        hospital_name = self.kwargs.get("hospital_name")
        if hospital_name:
            queryset = Hospital.objects.filter(
                hospital_name__icontains=hospital_name
            ).order_by("-modified_at")
        else:
            queryset = Hospital.objects.all().order_by("-modified_at")
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request):
        try:
            hospitals = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(hospitals)
            serializer = self.serializer_class(page, many=True)
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
            serializer = HospitalSerializer(data=request.data)
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
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class HospitalDetailView(APIView):
    """
    Retrieve, update or delete a hospital instance.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            data = Hospital.objects.get(pk=pk)
            return data
        except Hospital.DoesNotExist:
            return None

    def get(self, request, pk):
        try:
            hospital = self.get_object(pk)
            if hospital is not None:
                serializer = HospitalSerializer(hospital)
                return create_response_util.create_response_data(
                    message="success",
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                return create_response_util.create_response_data(
                    message="Hospital not found",
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
            hospital = self.get_object(pk)
            if hospital is not None:
                serializer = HospitalPutSerializer(hospital, data=request.data)
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

    def delete(self, request, pk):
        try:
            hospital = self.get_object(pk)
            if hospital is not None:
                hospital.is_active = False
                hospital.save()
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


class HospitalBranchView(APIView):
    """
    List all hospital branches, or create a new hospital branch.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            hospital_branches = HospitalBranch.objects.all()
            serializer = HospitalBranchSerializer(hospital_branches, many=True)
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
            serializer = HospitalBranchSerializer(data=request.data)
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
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class HospitalBranchDetailView(APIView):
    """
    Retrieve, update or delete a hospital branch instance.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            data = HospitalBranch.objects.get(pk=pk)
            return data
        except HospitalBranch.DoesNotExist:
            return None

    def get(self, request, pk):
        try:
            hospital_branch = self.get_object(pk)
            if hospital_branch is not None:
                serializer = HospitalBranchSerializer(hospital_branch)
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

    def put(self, request, pk):
        try:
            hospital_branch = self.get_object(pk)
            if hospital_branch is not None:
                serializer = HospitalBranchSerializer(
                    hospital_branch, data=request.data
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

    def delete(self, request, pk):
        try:
            hospital_branch = self.get_object(pk)
            if hospital_branch is not None:
                hospital_branch.is_active = False
                hospital_branch.save()
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


class TreatmentView(APIView):
    """
    List all treatments, or create a new treatment.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            treatments = Treatment.objects.all()
            serializer = TreatmentSerializer(treatments, many=True)
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
            serializer = TreatmentSerializer(data=request.data)
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
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class TreatmentDetailView(APIView):
    """
    Retrieve, update or delete a treatment instance.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            data = Treatment.objects.get(pk=pk)
            return data
        except Treatment.DoesNotExist:
            return None

    def get(self, request, pk):
        try:
            treatment = self.get_object(pk)
            if treatment is not None:
                serializer = TreatmentSerializer(treatment)
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

    def put(self, request, pk):
        try:
            treatment = self.get_object(pk)
            if treatment is not None:
                serializer = TreatmentSerializer(treatment, data=request.data)
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

    def delete(self, request, pk):
        try:
            treatment = self.get_object(pk)
            if treatment is not None:
                treatment.delete()
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


class DepartmentView(APIView):
    """
    List all departments, or create a new department.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            departments = Department.objects.all()
            serializer = DepartmentSerializer(departments, many=True)
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
            serializer = DepartmentSerializer(data=request.data)
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
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class DepartmentDetailView(APIView):
    """
    Retrieve, update or delete a department instance.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            data = Department.objects.get(pk=pk)
            return data
        except Department.DoesNotExist:
            return None

    def get(self, request, pk):
        try:
            department = self.get_object(pk)
            if department is not None:
                serializer = DepartmentSerializer(department)
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

    def put(self, request, pk):
        try:
            department = self.get_object(pk)
            if department is not None:
                serializer = DepartmentSerializer(department, data=request.data)
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

    def delete(self, request, pk):
        try:
            department = self.get_object(pk)
            if department is not None:
                department.delete()
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


class UploadChronicDiseaseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            file = request.FILES["file"]
            df = pd.read_excel(file, engine="openpyxl")
            for name in df.values:
                is_chr_cond = ChronicCondition.objects.filter(disease_name=name[0])
                if not is_chr_cond:
                    ChronicCondition.objects.create(disease_name=name[0])
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


class ChroniConditionAPIView(generics.ListAPIView):
    # permission_classes = [IsAuthenticated]
    queryset = ChronicCondition.objects.all().order_by("disease_name")
    serializer_class = CronicConditionSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    filterset_class = ChronicDiseaseFilter
    search_fields = ["disease_name"]

    def get_queryset(self, *args, **kwargs):
        qset = super().get_queryset(*args, **kwargs).order_by("-modified_at")
        return qset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request):
        try:
            chronic_data = self.filter_queryset(self.get_queryset())
            data = self.paginate_queryset(chronic_data)
            serializer = self.serializer_class(data, many=True)
            pages = self.get_paginated_response(serializer.data)
            # chronic_data = self.filter_queryset(self.get_queryset())
            # serializer = self.serializer_class(chronic_data, many=True)
            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=pages.data,
                errors=None,
            )
            # return Response(serializer.data)
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )

    def post(self, request):
        try:
            serializer = CronicConditionSerializer(data=request.data)
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
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class UploadNPIDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            file = request.FILES["file"]
            df = pd.read_csv(file)
            for i in df.values:
                is_npi = NPI.objects.filter(
                    npi_id=i[0],
                    endpoint_type=i[1],
                    endpoint_type_description=i[2],
                    endpoint=i[3],
                    affiliation=i[4],
                    endpoint_description=i[5],
                    affiliation_legal_business_name=i[6],
                    use_code=i[7],
                    use_description=i[8],
                    other_use_description=i[9],
                    content_type=i[10],
                    content_description=i[11],
                    other_content_description=i[12],
                    affiliation_address_line_one=i[13],
                    affiliation_address_line_two=i[14],
                    affiliation_address_city=i[15],
                    affiliation_address_state=i[16],
                    affiliation_address_country=i[17],
                    affiliation_address_postal_code=i[18],
                )
                if not is_npi:
                    obj = NPI.objects.create(
                        npi_id=i[0],
                        endpoint_type=i[1],
                        endpoint_type_description=i[2],
                        endpoint=i[3],
                        affiliation=i[4],
                        endpoint_description=i[5],
                        affiliation_legal_business_name=i[6],
                        use_code=i[7],
                        use_description=i[8],
                        other_use_description=i[9],
                        content_type=i[10],
                        content_description=i[11],
                        other_content_description=i[12],
                        affiliation_address_line_one=i[13],
                        affiliation_address_line_two=i[14],
                        affiliation_address_city=i[15],
                        affiliation_address_state=i[16],
                        affiliation_address_country=i[17],
                        affiliation_address_postal_code=i[18],
                    )
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


class StatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            hospital_created_date = list(
                Hospital.objects.values_list("created_at", flat=True)
            )
            hospital_dates = []
            for date in hospital_created_date:
                hospital_dates.append(
                    datetime.datetime.strptime(
                        date.date().strftime("%m/%d/%Y"), "%m/%d/%Y"
                    ).timestamp()
                )
            hospital_dates_counts = dict(Counter(hospital_dates))

            patient_created_date = list(
                Patient.objects.values_list("created_at", flat=True)
            )
            patient_dates = []
            for date in patient_created_date:
                patient_dates.append(
                    datetime.datetime.strptime(
                        date.date().strftime("%m/%d/%Y"), "%m/%d/%Y"
                    ).timestamp()
                )
            patient_dates_counts = dict(Counter(patient_dates))

            provider_created_date = list(
                Provider.objects.values_list("created_at", flat=True)
            )
            provider_dates = []
            for date in provider_created_date:
                provider_dates.append(
                    datetime.datetime.strptime(
                        date.date().strftime("%m/%d/%Y"), "%m/%d/%Y"
                    ).timestamp()
                )
            provider_dates_counts = dict(Counter(provider_dates))

            return create_response_util.create_response_data(
                message="success",
                status=status.HTTP_200_OK,
                data=[
                    {
                        "hospitals": [
                            {key: value for key, value in hospital_dates_counts.items()}
                        ]
                    },
                    {
                        "patient": [
                            {key: value for key, value in patient_dates_counts.items()}
                        ]
                    },
                    {
                        "doctor": [
                            {key: value for key, value in provider_dates_counts.items()}
                        ]
                    },
                ],
                errors=None,
            )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class GetHospitaDataListView(generics.ListCreateAPIView):
    renderer_classes = [ApiRenderer, BrowsableAPIRenderer]
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]
    queryset = Hospital.objects.all().order_by("-modified_at")
    serializer_class = HospitaldataListSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = HospitalFilter
    search_fields = [
        "hospital_name",
        "npi_id",
        "city",
        "hospital_status",
    ]

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request):
        try:
            hospitals = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(hospitals)
            serializer = self.serializer_class(
                page, many=True, context={"request": self.request}
            )
            pages = self.get_paginated_response(serializer.data)
            if pages is not None:
                serializer = self.serializer_class(page, many=True)
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


class HospitalRelatedUserView(APIView):
    serializer_class = HospitalRelatedUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            data = Hospital.objects.get(pk=pk)
            return data
        except Hospital.DoesNotExist:
            return None

    def get(self, request, pk):
        try:
            hospital = self.get_object(pk)
            if hospital is not None:
                care_mgrs = CareManager.objects.filter(hospital=hospital).values(
                    "user__id"
                )
                providers_objs = Provider.objects.filter(hospital=hospital).values(
                    "user__id"
                )
                practice_admins = PracticeAdmin.objects.filter(
                    hospital=hospital
                ).values("user__id")

                hospital_user_type = User.objects.filter(
                    Q(id__in=Subquery(care_mgrs))
                    | Q(id__in=Subquery(providers_objs))
                    | Q(id__in=Subquery(practice_admins))
                ).order_by("-modified_at")
                serializer = HospitalRelatedUserSerializer(
                    hospital_user_type, context={"hospital_obj": hospital}, many=True
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
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class HospitalBranchLocationView(APIView):
    # permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            hospital = Hospital.objects.get(pk=pk)
            return hospital
        except Hospital.DoesNotExist:
            return None

    def get(self, request, pk):
        try:
            hospital = self.get_object(pk)
            if hospital is not None:
                hospital_branch = hospital.hospital_branch.all().order_by(
                    "-modified_at"
                )
                serializer = HospitalBranchLocationSerializer(
                    hospital_branch, many=True
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
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class StaticsTestView(APIView):
    """
    List all departments, or create a new department.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            departments = Hospital.objects.all()
            serializer = HospitalTestSerializer(departments, many=True)
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


class MedicationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            medications = Medication.objects.all()
            serializer = MedicationSerializer(medications, many=True)
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
            serializer = MedicationSerializer(data=request.data)
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
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class MedicationOfPatienView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    filterset_class = MedicationFilter

    def get_queryset(self, *args, **kwargs):
        all_medications = self.request.query_params.get("all_medication")
        if all_medications is not None:
            queryset = Medication.objects.filter(patient_id=self.kwargs["patient_id"])
        else:
            queryset = Medication.objects.filter(
                patient_id=self.kwargs["patient_id"], midication_status="ACTIVE"
            ).order_by("-created_at")
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, patient_id):
        try:
            all_medications = self.request.query_params.get("all_medication")
            if all_medications is not None:
                medications = self.filter_queryset(
                    self.get_queryset(patient_id=patient_id)
                )
            else:
                medications = self.filter_queryset(
                    self.get_queryset(patient_id=patient_id)
                )[:5]
            serializer = MedicationSerializer(medications, many=True)
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


class MedicationUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, patient_id):
        try:
            patient = Patient.objects.get(pk=patient_id)
            return patient
        except Patient.DoesNotExist:
            return None

    def put(self, request, pk, patient_id):
        try:
            patient = self.get_object(patient_id)
            medications = Medication.objects.filter(id=pk, patient=patient).last()
            if medications is not None:
                serializer = MedicationSerializer(medications, data=request.data)
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
                    errors="Medication not found",
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PatientChronicDiseaseView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PatientChronicDiseaseCreateSerializer

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


class PatientChronicDiseaseUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PatientChronicDiseaseUpdateSerializer

    def get_object(self, patient_id):
        try:
            patient = Patient.objects.get(pk=patient_id)
            return patient
        except Patient.DoesNotExist:
            return None

    def put(self, request, patient_chronic_id, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                pcd = PatientChronicDisease.objects.filter(
                    pk=patient_chronic_id, patient_id=patient_id
                ).last()
                serializer = self.serializer_class(pcd, data=request.data)
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
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PatientChronicDiseaseListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PatientChronicDiseaseListSerializer

    def get_object(self, patient_id):
        try:
            patient = Patient.objects.get(pk=patient_id)
            return patient
        except Patient.DoesNotExist:
            return None

    def get(self, request, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                cd = ChronicCondition.objects.all()
                serializer = self.serializer_class(
                    cd, many=True, context={"patient_id": patient_id}
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


class PatientChronicDiseaseRetrieveView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PatientChronicDiseaseSerializer

    def get_object(self, patient_id):
        try:
            patient = Patient.objects.get(pk=patient_id)
            return patient
        except Patient.DoesNotExist:
            return None

    def get(self, request, patient_id):
        try:
            patient = self.get_object(patient_id)
            if patient is not None:
                pcd = ChronicCondition.objects.all()
                serializer = self.serializer_class(
                    pcd, many=True, context={"patient_id": patient_id}
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


class AssignPatientChronicDiseaseView(APIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = AssignChronicConditionSerializer

    def post(self, request):
        try:
            chronic_list = request.data.get("chronic")
            patient_id = request.data.get("patient")
            assign_patient_id = []
            assign_patient = PatientChronicDisease.objects.filter(patient=patient_id)
            for patient in assign_patient:
                assign_patient_id.append(patient.chronic.id)
                patient.delete()

            for chronic_disease in chronic_list:
                data = {"patient": patient_id, "chronic": chronic_disease}
                serializer = self.serializer_class(data=data)
                if serializer.is_valid():
                    serializer.save(is_active=False)
                else:
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.errors,
                        errors=None,
                    )
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


class ChronicDiseaseUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChronicConditionSerializer

    def get_object(self, chronic_id):
        try:
            chronic = ChronicCondition.objects.filter(id=chronic_id).last()
            return chronic
        except Patient.DoesNotExist:
            return None

    def delete(self, request, chronic_id):
        try:
            chronic = self.get_object(chronic_id)
            if chronic is not None:
                chronic.delete()
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

    def put(self, request, chronic_id):
        try:
            chronic = self.get_object(chronic_id)
            serializer = self.serializer_class(chronic, data=request.data)
            if serializer.is_valid():
                serializer.save()
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


class TaxonomyDescriptionView(generics.ListAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = NPITaxonomySerializer
    queryset = NPITaxonomy.objects.all()
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["provider_taxonomy_code"]

    def get_queryset(self, *args, **kwargs):
        queryset = NPITaxonomy.objects.all()
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request):
        try:
            qs = self.filter_queryset(self.get_queryset())
            serializer = self.serializer_class(qs, many=True)
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


class UnAssignPatientChronicDiseaseView(APIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = AssignChronicConditionSerializer

    def put(self, request):
        try:
            chronic_list = request.data.get("chronic")
            patient_id = request.data.get("patient")
            PatientChronicDisease.objects.filter(patient=patient_id).delete()
            for chronic_disease in chronic_list:
                data = {"patient": patient_id, "chronic": chronic_disease}
                serializer = self.serializer_class(data=data)
                if serializer.is_valid():
                    serializer.save(is_active=False)
                else:
                    return create_response_util.create_response_data(
                        message="success",
                        status=status.HTTP_200_OK,
                        data=serializer.errors,
                        errors=None,
                    )
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


class PatientMedicationChronicDiseaseListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PatientMedicationChronicDiseaseListSerializer

    def get(self, request):
        try:
            cd = MedicationChronicCondition.objects.all()
            serializer = self.serializer_class(cd, many=True)
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


class MedicationListView(generics.ListAPIView):
    serializer_class = MedicationListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
    )
    search_fields = ("medication_name",)

    def get_queryset(self, *args, **kwargs):
        patient_id = self.kwargs.get("patient_id")
        patient_id = Patient.objects.filter(pk=patient_id).last()
        queryset = Medication.objects.filter(patient=patient_id)
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def list(self, request, patient_id):
        try:
            medication = self.filter_queryset(self.get_queryset(patient=patient_id))
            data = self.paginate_queryset(medication)
            serializer = self.serializer_class(data, many=True)
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
