from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from django.utils.translation import gettext_lazy as _

from .forms import CustomUserChangeForm, CustomUserCreationForm

CustomUser = get_user_model()

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ['email', 'phone_number', 'first_name', 'last_name', 'is_staff']
    list_display_links = ['email', 'phone_number', 'first_name', 'last_name', 'is_staff']
    search_fields = ['email', 'phone_number', 'first_name', 'last_name']
    list_filter = ['is_staff']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
