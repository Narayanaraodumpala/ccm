from django.utils import timezone
from datetime import datetime

from rest_framework import serializers

from apps.account_manager.serializers import PatientSerializer
from apps.assessment.models import AppointmentSchedule, SelfManagementPlan, Assessment, AssessmentQuestionCategory, Question, PatientQuestionAnswer


class AppointmentScheduleSerializer(serializers.ModelSerializer):
    event_type = serializers.SerializerMethodField()

    class Meta:
        model = AppointmentSchedule
        fields = ["patient_name", "appointment_date_time", "description", "event_type"]

    def get_event_type(self, obj):
        if obj.appointment_date_time > timezone.now():
            return "UPCOMING"
        if obj.appointment_date_time < timezone.now():
            return "DUE"
        else:
            return "UNDEFINED"


class SelfManagementPlanSerializer(serializers.ModelSerializer):
    patient = PatientSerializer

    class Meta:
        model = SelfManagementPlan
        fields = ["note", "description", "patient"]


class AssessmentQuestionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentQuestionCategory
        fields = "__all__"


class AssessmentQuestionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ("question_category", "inquiry", "question_type","option_1", "option_2","option_3","option_4","option_5","ask","ask_description")


class GetQuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    class Meta:
        model = Question
        fields = ["id",'question_category','inquiry','question_type','ask','ask_description','options']
        
    def get_options(self, obj):
        options = {}
        option_1 = obj.option_1
        option_2 = obj.option_2
        option_3 = obj.option_3
        option_4 = obj.option_4
        option_5 = obj.option_5
        if obj.option_1:
            options['option_1'] = option_1
        if obj.option_2:
            options['option_2'] = option_2
        if obj.option_3:
            options['option_3'] = option_3
        if obj.option_4:
            options['option_4'] = option_4
        if obj.option_5:
            options['option_5'] = option_5            
        return options


class CreateAssessmentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ("date", "question_category", "assessment_status")


class CreateAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = "__all__" 


class ListAssessmentSerializer(serializers.ModelSerializer):
    question_category_id = serializers.SerializerMethodField()
    question_category = serializers.SerializerMethodField()
    assessment_status = serializers.SerializerMethodField()
    time_spent = serializers.SerializerMethodField()
    manual_time = serializers.SerializerMethodField()
  
    class Meta:
        model = Assessment
        fields = ["id", "question_category_id", "question_category", "start_date", "end_date", "date", "score", "assessment_status", "time_spent",
                  "patient", "action_taken", "manual_time", "severity"]

    def get_question_category_id(self, obj):
        return obj.question_category.id

    def get_question_category(self, obj):
        return obj.question_category.question_category

    def get_assessment_status(self, obj):
        return obj.get_assessment_status_display()
    
    def get_time_spent(self, obj):
        if obj.time_spent:
            return obj.time_spent.seconds // 60
        else:
            return None
        
    def get_manual_time(self, obj):
        if obj.manual_time:
            return obj.manual_time.seconds // 60
        else:
            return None      


class PatientQuestionAnswerSerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField()
    question_id = serializers.SerializerMethodField()
    manual_time = serializers.SerializerMethodField()
    action_taken = serializers.SerializerMethodField()
    

    class Meta:
        model = PatientQuestionAnswer
        fields = ("assessment", "patient", "question", "question_id", "answer", "action_taken", "manual_time")

    def get_question(self, obj):
        return obj.question.inquiry

    def get_question_id(self, obj):
        return obj.question.id
    
    def get_action_taken(self, obj):
        assessment_id = self.context["assessment_id"]
        assessment = Assessment.objects.filter(id = assessment_id ).last()
        action_taken = assessment.action_taken
        return action_taken
    
    def get_manual_time(self, obj):
        assessment_id = self.context["assessment_id"]
        assessment = Assessment.objects.filter(id = assessment_id ).last()
        manual_time = assessment.manual_time.seconds // 60
        return manual_time
    
    
class CreatePatientQuestionAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientQuestionAnswer
        fields = "__all__"


class CreatePatientQuestionAnswerCreateSerializer(serializers.Serializer):
    
    patient_question_answer = CreatePatientQuestionAnswerSerializer(many=True)
              
        

class PatientAnswerUpdateSerializer(serializers.ModelSerializer):
    # assessment = serializers.IntegerField()
    # patient = serializers.IntegerField()
    # answer = serializers.CharField(max_length=200)


    class Meta:
        model = PatientQuestionAnswer
        fields = ("assessment", "patient", "answer")
    
            
    # def validated_assessment(self, assessment):
    #     print(assessment)
    #     assessment_obj = 1
    #     return assessment_obj

    # def validate(self, data):
    #     assessment = data.get('assessment')
    #     patient = data.get('patient')
    #     if not PatientQuestionAnswer.objects.filter(assessment=assessment,patient=patient).exists():
    #         raise serializers.ValidationError("patient or assesment query does not match")
    #     return data
    #
    # def create(self, validated_data):
    #     return PatientQuestionAnswer(**validated_data)
    #
    # def update(self, instance, validated_data):
    #     breakpoint()
    #     for data in instance:
    #         data.answer = validated_data.get('answer',)
    #         data.save()
    #     return validated_data


class UpdateAssessmentMannualTimeViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ("manual_time", "action_taken")