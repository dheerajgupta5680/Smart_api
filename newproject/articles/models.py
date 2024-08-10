from django.contrib.auth.models import AbstractUser
from django.db import models
from django_cryptography.fields import encrypt

class CustomUser(AbstractUser):
    # Your custom fields here
    client_id = models.CharField(max_length=255, null=False, blank=False)
    totp = encrypt(models.CharField(max_length=255, null=False, blank=False))  # Encrypt TOTP as it's sensitive
    pin = encrypt(models.CharField(max_length=255, null=False, blank=False))  # Encrypt TOTP as it's sensitive
    