from django.contrib import admin
from import_export import resources, widgets, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

from apps.account_manager.models import (
    PracticeAdmin,
    Provider,
    CareManager,
    Communication,
    PatientProviderMapping, Patient, PatientSession

)
from apps.authentication.models import User


class PatientResource(resources.ModelResource):
    user = fields.Field(column_name='email', attribute='user', widget=ForeignKeyWidget(User, field='email'))

    def get_or_init_instance(self, instance_loader, row):
        instance, bool = super(PatientResource, self).get_or_init_instance(instance_loader, row)
        try:
            user_obj = User.objects.create(
                email=row['email'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                user_type="PATIENT"
            )
            instance.user = user_obj
            return instance, bool
        except Exception as e:
            print(e)

    class Meta:
        model = Patient
        import_id_fields = ('id',)
        fields = ['id', 'user', 'title', 'middle_name', 'dob', 'gender']


class ProviderResource(resources.ModelResource):
    user = fields.Field(column_name='email', attribute='user', widget=ForeignKeyWidget(User, field='email'))

    def get_or_init_instance(self, instance_loader, row):
        instance, bool = super(ProviderResource, self).get_or_init_instance(instance_loader, row)
        try:
            user_obj = User.objects.create(
                email=row['email'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                user_type="PROVIDER"
            )
            instance.user = user_obj
            return instance, bool
        except Exception as e:
            print(e)

    class Meta:
        model = Provider
        import_id_fields = ('id',)
        fields = ['id', 'user', 'gender', 'middle_name', 'contact_number', 'taxonomy_description'
                  , 'taxonomy_code_set', 'taxonomy_code', 'address_1', 'address_2'
                  , 'city', 'state', 'zip_code']


class PatientAdmin(ImportExportModelAdmin):
    resource_class = PatientResource
    list_display = ('user', 'hospital', 'gender', 'patient_status')
    search_fields = ('user__first_name',)
    class Meta:
        model = Patient


class CareManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'hospital')
    search_fields = ("user__first_name",)


class PatientProviderMappingAdmin(admin.ModelAdmin):
    list_display = ('patient', 'primary_provider', 'secondary_provider')
    search_fields = ('patient__user__first_name',)


class ProviderAdmin(ImportExportModelAdmin):
    resource_class = ProviderResource
    list_display = ('user', 'hospital', 'gender', 'provider_status')
    search_fields = ('user__first_name',)

    class Meta:
        model = Provider

# Register your models here.
admin.site.register(PracticeAdmin)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(Communication)
admin.site.register(CareManager, CareManagerAdmin)
admin.site.register(PatientProviderMapping, PatientProviderMappingAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(PatientSession)
