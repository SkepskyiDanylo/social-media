from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from user.models import User
from django.utils.translation import gettext_lazy as _

admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        "id",
        "email",
        "full_name",
        "is_staff",
        "is_superuser",
        "is_email_verified",
        "followers_count",
        "following_count",
        "status",
        "avatar_preview",
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "status", "avatar_preview", "picture")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_email_verified",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("Followers"), {"fields": ("followers", "followers_count", "following_count")}),
    )
    ordering = None
    list_filter = ("is_staff", "is_superuser", "is_email_verified")
    search_fields = ("email", "first_name", "last_name", "status")
    readonly_fields = ("followers_count", "following_count", "avatar_preview")

    def avatar_preview(self, obj):
        if obj.picture:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%;" />',
                obj.picture.url,
            )
        return "—"
    avatar_preview.short_description = "Avatar"
