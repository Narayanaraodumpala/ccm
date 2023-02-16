import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager

from rest_framework_simplejwt.tokens import RefreshToken


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        # extra_fields = {"is_staff": False, "is_superuser": False, **extra_fields}
        # if not email:
        #     raise ValueError("Users must have an email address")

        # user = User(email=email, **extra_fields)

        # if password:
        #     user.set_password(password)
        # else:
        #     user.set_unusable_password()

        # return user

        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # extra_fields = {**extra_fields, "is_staff": True, "is_superuser": True}

        # user = self.create_user(email=email, password=password, **extra_fields)

        # return user
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("user_type", "SUPERADMIN")
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class BaseModel(models.Model):
    """
    BaseModel:
    Containes DateTime for creation and updation'
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_at = models.DateTimeField(auto_now=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    modified_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        abstract = True


USERTYPE = (
    ("SUPERADMIN", "Super Admin"),
    ("PRACTICEADMIN", "Practice Admin"),
    ("PROVIDER", "Provider"),
    ("CAREMANAGER", "Care Manager"),
    ("PATIENT", "Patient"),
)


class User(AbstractUser, BaseModel):
    """
    User:
    Contains Information to store for user'
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    user_type = models.CharField(
        max_length=15, choices=USERTYPE, null=True, blank=True, default=None
    )
    system_id = models.UUIDField(default=uuid.uuid4, editable=False)
    profile_pic = models.ImageField(upload_to="profile_pic/", null=True, blank=True)

    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return str(self.email)
    
    def __unicode__(self):
        return self.id

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}


class MyProfile(BaseModel):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_no = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.first_name
