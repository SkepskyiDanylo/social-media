from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from social_media_api import settings
from user.models import User


class EmptySerializer(serializers.Serializer):
    pass


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "is_email_verified",
            "is_staff",
            "is_superuser",
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {"input_type": "password"},
            }
        }
        read_only_fields = ("id", "is_staff", "is_superuser", "is_email_verified")

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise ValidationError(e.messages)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        if not settings.USE_EMAIL_VERIFICATION:
            user.is_email_verified = True
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    uid = serializers.CharField()
    token = serializers.CharField()

    class Meta:
        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {"input_type": "password"},
            }
        }
