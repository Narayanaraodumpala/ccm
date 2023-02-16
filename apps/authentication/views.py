import markupsafe

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from rest_framework.permissions import IsAuthenticated
from apps.account_manager import create_response_util
from apps.account_manager.utils import SendMail
from apps.authentication.models import MyProfile
from apps.authentication.serializers import (
    UserLoginSerializer,
    ResetPasswordViaEmailSerializer,
    SetNewPasswordSerializer,
    MyProfileSerializer,
    UpdateUserProfileImageSerializer,
    ChangePasswordSerializer
)

from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response

User = get_user_model()


def create_user(data):
    password = data["password"]
    if User.objects.filter(email=data["email"]).exists():
        raise ValueError("This Email already exist.")
    user = User(
        email=data["email"],
    )
    user.set_password(password)
    user.save()
    return user


class UserLoginApi(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        try:
            data = request.data
            serializer = self.serializer_class(data=data, context={'request': request})
            if serializer.is_valid():
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


# Forgot Password
class RequestPasswordResetEmail(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = ResetPasswordViaEmailSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            email = request.data["email"]
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                SendMail.user_send_password_reset_email(user)
                # thread = Thread(target=SendMail.user_send_password_reset_email, args=(data,))
                # thread.start()
                # message = "Check your email to reset your password"
                return create_response_util.create_response_data(
                    message="success", status=status.HTTP_200_OK, data=None, errors=None
                )
            else:
                return create_response_util.create_response_data(
                    message="failed",
                    status=status.HTTP_400_BAD_REQUEST,
                    data=None,
                    errors="User not found",
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class PasswordTokenCheckAPIView(generics.GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                message = "token is not valid, please check the new one"
                return create_response_util.create_response_data(
                    status.HTTP_401_UNAUTHORIZED, message
                )
            data = {"uidb64": uidb64, "token": token}
            # return create_response_util.create_response_data(status.HTTP_200_OK, message, data=data)
            return create_response_util.create_response_data(
                message="success", status=status.HTTP_200_OK, data=data, errors=None
            )

        except DjangoUnicodeDecodeError as indentifier:
            message = "token is not valid, please check the new one"
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=message,
            )


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                message = "Password is reset successfully"
                return create_response_util.create_response_data(
                    message=message,
                    status=status.HTTP_200_OK,
                    data=serializer.data,
                    errors=None,
                )
            else:
                message = "Password is reset Failed"
                return create_response_util.create_response_data(
                    status.HTTP_400_BAD_REQUEST,
                    message,
                    create_response_util.HTTP_CODE_TO_RENDER["400"],
                )

        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class MyProfileView(APIView):
    """
    create and get all My Profiles
    """

    serializer = MyProfileSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = MyProfile.objects.all()
            if data:
                serializer = self.serializer(data, many=True)
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

    def post(self, request):
        try:
            serializer = MyProfileSerializer(data=request.data)
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
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )


class MyProfileViewDetails(APIView):
    """
    get, update and delete My Profiles
    """

    serializer = MyProfileSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            data = MyProfile.objects.filter(id=id)
            if data:
                serializer = self.serializer(data, many=True)
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
            data = MyProfile.objects.filter(id=id).first()
            if data:
                serializer = self.serializer(data, data=request.data)
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
                    errors=None,
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
            if id:
                profile = MyProfile.objects.filter(id=id).last()
                profile.delete()
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


class UpdateUserProfileImageView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, id):
        try:
            user = User.objects.filter(id=id).first()
            if user:
                serializer = UpdateUserProfileImageSerializer(user, data=request.data)
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
                    errors=None,
                )
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )



class ChangePassword(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)
   
    def get_object(self, queryset=None):
        obj = self.request.user
        return obj
   
    def put(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            serializer = self.serializer_class(data=request.data,context={'request':request})
            if serializer.is_valid():
                # set_password also hashes the password that the user will get
                self.object.set_password(serializer.data.get("new_password"))
                self.object.save()
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
                    errors=serializer.errors,
                ) 
        except Exception as e:
            return create_response_util.create_response_data(
                message="failed",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data=None,
                errors=str(e),
            )  