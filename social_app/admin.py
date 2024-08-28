from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from social_app.models.user import User
from social_app.models.friend_request import FriendRequest


class UserAdmin(BaseUserAdmin):
    list_display = ("email", "first_name", "last_name", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active")
    fieldsets = (
        (None, {"fields": ("email", "password", "username")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Important dates", {"fields": ("last_login",)}),
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
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    filter_horizontal = ()


class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ("from_user", "to_user", "status")
    list_filter = ("status",)
    search_fields = ("from_user__email", "to_user__email")
    ordering = ("from_user", "to_user")


admin.site.register(User, UserAdmin)
admin.site.register(FriendRequest, FriendRequestAdmin)
admin.site.unregister(Group)
