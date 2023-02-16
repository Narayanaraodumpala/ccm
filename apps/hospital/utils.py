import django_filters
from django_filters import OrderingFilter, filters, DateFromToRangeFilter

from apps.account_manager.models import CareManager, PracticeAdmin, Provider
from apps.hospital.models import ChronicCondition, Medication


def user_type_hospital_exists(hospital, user):
        if user.user_type == "CAREMANAGER":
            related_cm_of_hospital = CareManager.objects.filter(hospital=hospital)
            if related_cm_of_hospital:
                return True, user.user_type
                
        elif user.user_type == "PROVIDER":
            related_cm_of_hospital = Provider.objects.filter(hospital=hospital)
            if related_cm_of_hospital:
                return True, user.user_type

        elif user.user_type == "PRACTICEADMIN":
            related_cm_of_hospital = PracticeAdmin.objects.filter(hospital=hospital)
            if related_cm_of_hospital:
                return True, user.user_type


class ChronicDiseaseFilter(django_filters.FilterSet):
    order_by_field = 'ordering'
    ordering = OrderingFilter(
        fields=(
            ("id", "id"),
            ("disease_name", "disease_name")
        )
        )
    class Meta:
        model = ChronicCondition
        fields = ['id']

class MedicationFilter(django_filters.FilterSet):
    from_date = filters.DateFilter(field_name='created_at', label='from_date', lookup_expr='gte')
    to_date = filters.DateFilter(field_name='created_at', label='to_date', lookup_expr='lte')

    order_by_field = 'ordering'
    ordering = OrderingFilter(
        fields=(
            ("id", "id"),
            ("created_at", "created_at")
        ),
    )

    class Meta:
        model = Medication
        fields = ['id', 'created_at']


class FilterMdeication(django_filters.FilterSet):
    medication_name = django_filters.CharFilter(lookup_expr = 'icontains')