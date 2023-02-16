import django_filters
from django_filters import OrderingFilter, filters, DateFromToRangeFilter

from apps.assessment.models import Assessment


class AssessmentFilter(django_filters.FilterSet):

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
        model = Assessment
        fields = ['id', 'created_at']