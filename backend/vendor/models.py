from django.db import models
from user.models import *
from django.conf import settings

# Create your models here.

class Tea(models.Model):
    name = models.CharField(max_length=10, null=True, blank=True)
    price = models.CharField(max_length=10,null = True, blank=True)
    quantity = models.IntegerField(default=0)



class Vendor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tea = models.ForeignKey(Tea, on_delete=models.CASCADE,blank=True,null=True)



class Transaction(models.Model):
    from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    to_user = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    amount = models.CharField(max_length=10)
    quantity = models.IntegerField()
    shipping_address = models.CharField(max_length=255, null=True, blank=True)