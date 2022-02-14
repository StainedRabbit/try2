from django.contrib import admin
from app.models import *

admin.site.register(Remittance)
admin.site.register(Sale)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Adjustment)
admin.site.register(Price)
admin.site.register(Procurement)
admin.site.register(Debit)
admin.site.register(CutOff)
admin.site.register(Supplier)


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                    "first_name",
                    "middle_name",
                    "last_name",
                    "credit_line",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )

    list_display = (
        "email",
        "first_name",
        "middle_name",
        "last_name",
        "credit_line",
        "is_staff",
        "last_login",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("email",)
    ordering = ("email",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )


admin.site.register(User, UserAdmin)

# Register your models here.
