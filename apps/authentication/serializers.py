from django.utils.encoding import force_str
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from apps.authentication.models import MyProfile
from apps.account_manager import utils

from rest_framework import serializers


User = get_user_model()


class UserLoginSerializer(serializers.ModelSerializer):
    id = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    first_name = serializers.EmailField(required=False)
    last_name = serializers.EmailField(required=False)
    password = serializers.CharField(required=True)
    tokens = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    user_type = serializers.CharField(read_only=True)
    system_id = serializers.CharField(required=False)
    user_type_non_caps = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "tokens",
            "refresh_token",
            "email",
            "first_name",
            "last_name",
            "system_id",
            "password",
            "user_type",
            "user_type_non_caps"
        ]

    def validate(self, attrs):
        email = attrs.get("email", None)
        request = self.context.get("request", None)
        if email:
            email = email.lower()
        password = attrs.get("password")
        system_id = attrs.get("system_id", None)

        result, message, email = utils.Validator.is_valid_user(
            email, password, system_id, request
        )
        if not result:
            raise serializers.ValidationError("Invalid Credentials")
        if result:
            user, user_type = utils.Validator.get_user_instance(email)
            user_type_non_caps =  user.get_user_type_display()
            return {
                "id":user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "user_type": user_type,
                "tokens": user.tokens().get("access"),
                "refresh_token": user.tokens().get("refresh"),
                "password": user.password,
                "user_type_non_caps":user_type_non_caps
                
            }


class ResetPasswordViaEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=68, write_only=True, required=True)
    confirm_password = serializers.CharField(
        max_length=68, write_only=True, required=True
    )
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ["new_password", "confirm_password", "token", "uidb64"]

    def validate(self, validated_data):
        try:
            new_password = validated_data.get("new_password")
            confirm_password = validated_data.get("confirm_password")
            token = validated_data.get("token")
            uidb64 = validated_data.get("uidb64")
            if new_password != confirm_password:
                raise serializers.ValidationError(
                    "new password and confirm password does not match"
                )
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if PasswordResetTokenGenerator().check_token(user, token):
                user.set_password(new_password)
                user.save()
                return validated_data
            else:
                raise serializers.ValidationError("The Reset Link Is Invalid")

        except Exception as e:
            raise serializers.ValidationError("The Reset Link Is Invalid")
        return super().validate(validated_data)


class MyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyProfile
        fields = "__all__"


class UpdateUserProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_pic']
class ChangePasswordSerializer(serializers.Serializer):
    old_password    = serializers.CharField(required=True)
    new_password    = serializers.CharField(required=True)
    confirm_password= serializers.CharField(required=True)

    def validate(self, validated_data):
        request = self.context.get('request')
        password = validated_data.get('new_password')
        confirm_password = validated_data.get('confirm_password')
        old_password = validated_data.get('old_password')
        if not request.user.check_password(old_password):
            raise Exception("Old Password Does Not Match!")
        if password != confirm_password:
            raise Exception("Password does not match.")  
        if len(password) < 5:
            raise Exception("The password must be at least 8 characters.")   
        return validated_data


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']
