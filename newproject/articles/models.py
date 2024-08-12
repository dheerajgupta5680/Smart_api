from django.contrib.auth.models import AbstractUser
from django.db import models
from django_cryptography.fields import encrypt
from django.utils.timezone import now

class CustomUser(AbstractUser):
    # Your custom fields here
    clientID = models.CharField(max_length=255, null=False, blank=False)
    apiKey = models.CharField(max_length=255, null=False, blank=False)
    pin = encrypt(models.CharField(max_length=255, null=False, blank=False))  # Encrypt TOTP as it's sensitive
    token = encrypt(models.CharField(max_length=255, null=False, blank=False))

class OrderRecord(models.Model):
    tradingsymbol = models.CharField(max_length=20)
    transactiontype = models.CharField(max_length=4)  # BUY or SELL
    exchange = models.CharField(max_length=10)
    ordertype = models.CharField(max_length=10)
    producttype = models.CharField(max_length=10)
    price = models.FloatField()
    quantity = models.IntegerField()
    orderid = models.CharField(max_length=30)
    date = models.DateTimeField(default=now, editable=False)