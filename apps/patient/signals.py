from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver

from apps.hospital.models import Patient
from apps.patient.models import ProgramInformation, BMI, BloodPressure, BloodGlucose, PulseOx, HBA1C, Cholesterol, Notes, PatientOutreach, PatientCallLog, PatientOutreach, AnnualWellnessVist, ScreeningName

@receiver(post_save, sender=Patient)
def create_vitals(sender, instance, created, **kwargs):
    if created:
        # ProgramInformation.objects.create(patient=instance)
        BMI.objects.create(patient=instance, is_active=False)
        BloodPressure.objects.create(patient=instance, is_active=False)
        BloodGlucose.objects.create(patient=instance, is_active=False)
        PulseOx.objects.create(patient=instance, is_active=False)
        HBA1C.objects.create(patient=instance, is_active=False)
        Cholesterol.objects.create(patient=instance, is_active=False)
        Notes.objects.create(patient=instance, is_active=True)
        
        
        
# @receiver(post_save, sender=PatientOutreach)
# def create_call_logs(sender, instance, created, **kwargs):
    
#     if created:
#         PatientCallLog.objects.create(
#             agenda =instance.time_spent, 
#             patient=instance.patient,
#             call_duration=instance.time_spent, 
#             call_status="COMPLETED", 
#             call_type="OUTREACH"
#             )

# @receiver(pre_save, sender=PatientOutreach)
# def create_outreach(sender, instance, **kwargs):
#         print("PUT triggered")
#         PatientOutreach.objects.create(
#             patient=instance.patient,
#             contact_date=instance.schedule_follow_up_date,
#             schedule_follow_up_date=None,
#             contact_type=instance.contact_type,
#             resolution_action=instance.resolution_action,
#             outcome=instance.outcome,
#             provider=instance.provider,
#             time_spent=None,
#             notes=None,
#             care_program=instance.care_program,
#             care_program_from_date=instance.care_program_from_date,
#             care_program_to_date=instance.care_program_to_date,
#             care_member=instance.care_member,
#             patientoutreach_status=instance.patientoutreach_status,
#             outreach_status=instance.outreach_status,
#         )


@receiver(post_save, sender=Patient)
def create_vitals(sender, instance, created, **kwargs):
    if created:
        screening_name_1 = ScreeningName.objects.filter(id=1).first()
        screening_name_2 = ScreeningName.objects.filter(id=2).first()
        screening_name_3 = ScreeningName.objects.filter(id=3).first()
        screening_name_4 = ScreeningName.objects.filter(id=4).first()
        screening_name_5 = ScreeningName.objects.filter(id=5).first()
        screening_name_6 = ScreeningName.objects.filter(id=6).first()
        screening_name_6 = ScreeningName.objects.filter(id=6).first()
        screening_name_7 = ScreeningName.objects.filter(id=7).first()
        screening_name_8 = ScreeningName.objects.filter(id=8).first()
        screening_name_9 = ScreeningName.objects.filter(id=9).first()
        screening_name_10 = ScreeningName.objects.filter(id=10).first()
        screening_name_11 = ScreeningName.objects.filter(id=11).first()
        screening_name_12 = ScreeningName.objects.filter(id=12).first()
        # screening_name_13 = ScreeningName.objects.filter(id=13).first()
        screening_name_14 = ScreeningName.objects.filter(id=14).first()
        screening_name_15 = ScreeningName.objects.filter(id=15).first()
        screening_name_16 = ScreeningName.objects.filter(id=16).first()
        screening_name_17 = ScreeningName.objects.filter(id=17).first()
        screening_name_18 = ScreeningName.objects.filter(id=18).first()
        screening_name_19 = ScreeningName.objects.filter(id=19).first()
        screening_name_20 = ScreeningName.objects.filter(id=20).first()
        screening_name_21 = ScreeningName.objects.filter(id=21).first()
        
        
        AnnualWellnessVist.objects.create(
            patient=instance, 
            services_and_Screening_name=screening_name_1, 
            who="Men ages 65-75 if a smoker",
            often="Once", 
            need=False,
            )
        
        AnnualWellnessVist.objects.create(
            patient=instance, 
            services_and_Screening_name=screening_name_2, 
            who="All Adults",
            often="Screening once a year if no alcohol misuse.Counseling up to 4 face-to-face sessions.", 
            need=False,
            )
        
        AnnualWellnessVist.objects.create(
            patient=instance, 
            services_and_Screening_name=screening_name_3, 
            who="People at risk for osteoporosis",
            often="Once every 24 months", 
            need=False,
            )
        
        AnnualWellnessVist.objects.create(
            patient=instance, 
            services_and_Screening_name=screening_name_4, 
            who="All Adults",
            often="Once every 5 year", 
            need=False,
            )
        
        
        AnnualWellnessVist.objects.create(
            patient=instance, 
            services_and_Screening_name=screening_name_5, 
            who="All Adults 50 and olders",
            often="Once every 12 months", 
            need=False,
            )
        
        AnnualWellnessVist.objects.create(
            patient=instance, 
            services_and_Screening_name=screening_name_6, 
            who="",
            often="Once every 48 months", 
            need=False,
            )

        AnnualWellnessVist.objects.create(
            patient=instance, 
            services_and_Screening_name=screening_name_7, 
            who="",
            often="every 18 months", 
            need=False,
            )

        
        AnnualWellnessVist.objects.create(
            patient=instance, 
            services_and_Screening_name=screening_name_8, 
            who="All Audlts",
            often="Once a year done if done in a primary care office able to provide treatment & referral ", 
            need=False,
            )


        
        AnnualWellnessVist.objects.create(
            patient=instance, 
            services_and_Screening_name=screening_name_9, 
            who="All Audlts at risk",
            often="Dependin on your test results, up to two times a year-may require copay", 
            need=False,
            )
        

        AnnualWellnessVist.objects.create(
            patient=instance, 
            services_and_Screening_name=screening_name_10, 
            who="Audlts at high rick for claucoma",
            often="Once every 12 months-requires copay", 
            need=False,
            )

        AnnualWellnessVist.objects.create(
            patient=instance, 
            services_and_Screening_name=screening_name_11, 
            who="Audlts at high rick for HIV infection",
            often="Every year, if at risk or if requested", 
            need=False,
            
            
            )

        AnnualWellnessVist.objects.create(
            patient=instance, 
            services_and_Screening_name=screening_name_12, 
            who="Woman over 40",
            often="Every 2 yeara", 
            need=False,
            )
        
        # AnnualWellnessVist.objects.create(
        #     patient=instance, 
        #     services_and_Screening_name=screening_name_13, 
        #     who="Woman over 40",
        #     often="3 hours of counselling the first year 2 hours every year after that", 
        #     need=False,
        #     date_of_last_services=instance.created_at
        #     )

        AnnualWellnessVist.objects.create(
            patient=instance, 
            services_and_Screening_name=screening_name_14, 
            who="All Audlts",
            often="Screening once a year Counseling if BMI is > 30", 
            need=False,
            
            
            )

        AnnualWellnessVist.objects.create(
            patient=instance, 
            services_and_Screening_name=screening_name_15, 
            who="All Woman",
            often="Once every 24 months once every 12 months if at risk", 
            need=False,
            )
        
        AnnualWellnessVist.objects.create(
            patient=instance, 
            services_and_Screening_name=screening_name_16, 
            who="Man over 50",
            often="Shared decision with your doctor-may require copay", 
            need=False,
            )
        
        AnnualWellnessVist.objects.create(
            patient=instance, 
            services_and_Screening_name=screening_name_17, 
            who="Adults sho use tobacco with no tobacco-related illnesses",
            often="up to 8 visits in a12 month period", 
            need=False,
            
            )
        
        AnnualWellnessVist.objects.create(
            patient=instance, 
            services_and_Screening_name=screening_name_18, 
            who="All Adults 50 and older",
            often="Once", 
            need=False,
            )
        
        AnnualWellnessVist.objects.create(
            patient=instance, 
            services_and_Screening_name=screening_name_19, 
            who="",
            often="Once every flu season", 
            need=False,
            )
        

        AnnualWellnessVist.objects.create(
            patient=instance, 
            services_and_Screening_name=screening_name_20, 
            who="",
            often="Once", 
            need=False,
            )
        
        AnnualWellnessVist.objects.create(
            patient=instance, 
            services_and_Screening_name=screening_name_21, 
            who="People with Medicare",
            often="Every year", 
            need=False,
            )