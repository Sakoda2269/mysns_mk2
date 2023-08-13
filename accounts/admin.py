from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import Follower

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            ("Permissions"),
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (("Important dates"), {"fields": ("username", "usertag", "last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2"),
            },
        ),
    )
    list_display = ("email", "username", "is_staff", "id")
    list_filter = ("is_staff", "is_superuser", "groups")
    search_fields = ("email", "username")
    ordering = ("email", "username",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )

CustomUser = get_user_model()


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Follower)
