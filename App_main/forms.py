from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

from App_main.models import PoliceProfile


class SignUpForm(UserCreationForm):
    username = forms.CharField(required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'PoliceID'}))
    email = forms.CharField(required=True,
                            widget=forms.TextInput(attrs={'placeholder': 'Email'}))

    present_address = forms.CharField(required=True,
                                      widget=forms.TextInput(attrs={'placeholder': 'Present Address'}))
    permanent_address = forms.CharField(required=True,
                                        widget=forms.TextInput(attrs={'placeholder': 'Permanent Address'}))
    date_of_birth = forms.CharField(required=True,
                                        widget=forms.TextInput(attrs={'type': 'date'}))

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'first_name', 'last_name', 'email', 'username', 'password1', 'password2', 'display_name', 'date_of_birth',
            'present_address', 'permanent_address', 'zip_code', 'city', 'mobile_phone', 'photo',)


class PoliceProfileForm(forms.ModelForm):
    class Meta:
        model = PoliceProfile
        exclude = ('user',)
