from django.contrib import admin
from apps.hospital.models import *

from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin


class HospitalAdmin(admin.ModelAdmin):
    list_display = ('hospital_name', 'npi_id', 'hospital_status')


class HospitalBranchAdmin(admin.ModelAdmin):
    list_display = ('hospital', 'branch_name', 'location')


class MedicationAdmin(admin.ModelAdmin):
    list_display = ('medication_name', 'frequency', 'prescriber')


class NPITaxonomyResource(resources.ModelResource):
    def init_instance(self, row, *args, **kwargs):
        try:
            instance = super().init_instance(*args, **kwargs)
            return instance
        except Exception as e:
            print(row)
            print(e)

    class Meta:
        model = NPITaxonomy


class NPITaxonomyAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = NPITaxonomyResource

    list_display = ['id', 'medicare_specialty_code', 'provider_taxonomy_code', 'provider_taxonomy_description']

    class Meta:
        model = NPITaxonomy


admin.site.register(NPITaxonomy, NPITaxonomyAdmin)
admin.site.register(Hospital, HospitalAdmin)
admin.site.register(HospitalBranch, HospitalBranchAdmin)
admin.site.register(Treatment)
admin.site.register(Department)
admin.site.register(ChronicCondition)
admin.site.register(Appointment)
admin.site.register(Medication, MedicationAdmin)
admin.site.register(PatientChronicDisease)
admin.site.register(MedicationChronicCondition)
