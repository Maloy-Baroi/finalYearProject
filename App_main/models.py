from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    display_name = models.CharField(verbose_name=_("Display name"), max_length=30,
                                    help_text=_("Will be shown e.g. when commenting"))
    date_of_birth = models.DateField(verbose_name=_("Date of birth"), blank=True, null=True)
    present_address = models.CharField(verbose_name=_("Address line 1"), max_length=1024, blank=True, null=True)
    permanent_address = models.CharField(verbose_name=_("Address line 2"), max_length=1024, blank=True, null=True)
    zip_code = models.CharField(verbose_name=_("Postal Code"), max_length=12, blank=True, null=True)
    city = models.CharField(verbose_name=_("City"), max_length=1024, blank=True, null=True)
    phone_regex = RegexValidator(regex=r"^\+?(88)01[3-9][0-9]{8}$", message=_(
        "Enter a valid international mobile phone number starting with +(country code)"))
    mobile_phone = models.CharField(validators=[phone_regex], verbose_name=_("Mobile phone"), max_length=17, blank=True,
                                    null=True)
    photo = models.ImageField(verbose_name=_("Photo"), upload_to='photos/', default='photos/default-user-avatar.png')

    class Meta:
        ordering = ['last_name']

    def __str__(self):
        return f"{self.username}: {self.first_name} {self.last_name}"


class PoliceProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="police")
    position = models.CharField(max_length=255)
    MaritalStatus = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CriminalLocation(models.Model):
    name = models.CharField(max_length=255)
    national_id = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    picture = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']


class Suspected(models.Model):
    name = models.CharField(max_length=255)
    national_id = models.CharField(max_length=255, default=None)
    address = models.CharField(max_length=255)
    picture = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class File(models.Model):
    file = models.FileField(blank=False, null=False)
    remark = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
