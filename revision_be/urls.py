"""revision_be URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from revision_be.settings import env

# Django Admin settings
admin.site.site_header = "Welcome, To Revision Super Django admin"
admin.site.site_title = "Revision Super Admin"


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/account/manager/", include("apps.account_manager.urls")),
    path("api/v1/assessment/", include("apps.assessment.urls")),
    path("api/v1/authentication/", include("apps.authentication.urls")),
    path("api/v1/hospital/", include("apps.hospital.urls")),
    path("api/v1/patient/", include("apps.patient.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


schema_view = get_schema_view(
    openapi.Info(
        title="Revision API",
        default_version="v1",
        description="Swagger Documentation of the revision api's ",
        contact=openapi.Contact(email="ashwin@thoughtwin.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

CURRENT_ENV = env("ENV")
ALLOWED_ENV_TO_SHOW_SWAGGER = ["LOCAL", "STAGING"]

if CURRENT_ENV in ALLOWED_ENV_TO_SHOW_SWAGGER:
    urlpatterns += [
        path(
            "revision/documentation/swagger/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger",
        ),
    ]
