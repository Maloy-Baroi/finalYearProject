from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, PoliceProfile, Suspected, File, CriminalLocation


class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = CustomUser
    list_display = ['pk', 'email', 'username', 'first_name', 'last_name']
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('display_name', 'date_of_birth', 'present_address', 'permanent_address',
                           'zip_code', 'city', 'mobile_phone', 'photo',)}),
    )
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': (
                    'display_name', 'date_of_birth', 'present_address', 'permanent_address', 'zip_code', 'city', 'mobile_phone',
                    'photo',)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(PoliceProfile)
admin.site.register(CriminalLocation)
admin.site.register(Suspected)
admin.site.register(File)
