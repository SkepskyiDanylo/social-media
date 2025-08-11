import logging
import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, viewsets, status
from rest_framework.generics import (
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
    get_object_or_404,
)
from rest_framework.response import Response


from social_media_api import settings
from user.models import User
from user.permissions import IsAdmin
from user.serializers import (
    UserSerializer,
    RequestPasswordResetSerializer,
    SetNewPasswordSerializer,
    EmptySerializer,
)

logger = logging.getLogger(__name__)


@extend_schema(tags=["User"])
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)


@extend_schema(tags=["Me"])
class UserRegister(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save()
        uid = str(user.id)
        if settings.USE_EMAIL_VERIFICATION:
            token = default_token_generator.make_token(user)
            link = f"{settings.FRONTEND_URL}/email-activate/{uid}/{token}/"
            send_mail(
                "Activate your account",
                f"Please activate your account: {link}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )


@extend_schema(tags=["Me"])
class ActivateAccountView(generics.RetrieveAPIView):
    serializer_class = EmptySerializer

    def get(self, request, uid=None, token=None):
        try:
            uid = uuid.UUID(uid)
            user = User.objects.get(pk=uid)
        except Exception:
            return Response(
                {"detail": _("Invalid link.")}, status=status.HTTP_400_BAD_REQUEST
            )

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response(
                {"detail": _("Account activated.")}, status=status.HTTP_200_OK
            )
        return Response(
            {"detail": _("Token invalid or expired.")}, status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(tags=["Me"])
class PasswordResetView(generics.GenericAPIView):
    serializer_class = RequestPasswordResetSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = get_object_or_404(get_user_model(), email=email)
        if user:
            uid = str(user.id)
            token = default_token_generator.make_token(user)
            link = f"{settings.FRONTEND_URL}/reset-password-confirm/{uid}/{token}/"
            send_mail(
                "Reset your password",
                f"Use this link to reset your password: {link}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
        return Response(
            {"detail": _("The reset link has been sent.")}, status=status.HTTP_200_OK
        )


@extend_schema(tags=["Me"])
class CheckPasswordTokenView(generics.RetrieveAPIView):

    def get(self, request, uid=None, token=None):
        try:
            uid = uuid.UUID(uid)
            user = User.objects.get(pk=uid)
        except (get_user_model().DoesNotExist, ValueError):
            return Response(
                {"valid": False, "detail": _("Invalid link.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        valid = default_token_generator.check_token(user, token)
        return Response(
            {"valid": valid},
            status=status.HTTP_200_OK if valid else status.HTTP_400_BAD_REQUEST,
        )


@extend_schema(tags=["Me"])
class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    http_method_names = ["post"]

    def patch(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return Response(
                {"detail": _("Invalid uid.")}, status=status.HTTP_400_BAD_REQUEST
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": _("Token invalid or expired")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(password)
        user.save()
        return Response(
            {"detail": _("Password reset successful.")}, status=status.HTTP_200_OK
        )


@extend_schema(tags=["Me"])
class MyProfileView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.none()
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user
