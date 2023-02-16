from django.urls import path
from apps.authentication import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("login/", views.UserLoginApi.as_view(), name="user-login"),
    # Forget Password
    path(
        "request-reset-email/",
        views.RequestPasswordResetEmail.as_view(),
        name="request-reset-email",
    ),
    path(
        "confirm-password/<uidb64>/<token>/",
        views.PasswordTokenCheckAPIView.as_view(),
        name="confirm-password",
    ),
    path(
        "password-reset-complete/",
        views.SetNewPasswordAPIView.as_view(),
        name="password-reset-complete",
    ),
    path("my_profile/", views.MyProfileView.as_view()),
    path("my_profile/<int:id>/", views.MyProfileViewDetails.as_view()),
    path("update/profile_pic/<str:id>/", views.UpdateUserProfileImageView.as_view()),
    
    path('change/password/', views.ChangePassword.as_view()), 
]
