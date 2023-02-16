from django.db.models.signals import post_save
from django.dispatch import receiver

# from apps.hospital.models import Medication, PatientChronicDisease


# @receiver(post_save, sender=Medication)
# def create_patient_chronic_condition(sender, instance, created, **kwargs):
#     try:
#         if created:
#             if instance.chronic_condition:
#                 PatientChronicDisease.objects.create(patient=instance.patient, chronic=instance.chronic_condition)
#             else:
#                 pass
#     except Exception as e:
#         print(f"create_patient_chronic_condition throws error : {e}")
