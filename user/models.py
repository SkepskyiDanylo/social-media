import os
import uuid

from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from social_media.models import BaseModel


# noinspection PySimplifyBooleanCheck
class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


def user_picture(instance: "User", filename: str) -> str:
    ext = filename.split(".")[-1]
    filename = f"{instance.email}-{uuid.uuid4()}.{ext}"
    return os.path.join("images", "users", filename)


class User(BaseModel, AbstractUser):
    username = None
    email = models.EmailField(_("Email address."), unique=True)
    is_email_verified = models.BooleanField(default=False)
    picture = models.ImageField(upload_to=user_picture, null=True, blank=True)
    bio = models.CharField(_("Bio"), max_length=255, null=True, blank=True)
    link = models.URLField(_("Link"), null=True, blank=True)
    status = models.CharField(_("Status"), max_length=50, null=True, blank=True)
    followers = models.ManyToManyField(
        "self",
        related_name="following",
        symmetrical=False,
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    @cached_property
    def followers_count(self):
        return self.followers.count()

    @cached_property
    def following_count(self):
        return self.following.count()

    def __str__(self):
        return self.email
