from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class Users(AbstractUser):
    secret_key = models.CharField(max_length=128, unique=True, null=True, default='')
    qrcode_url = models.CharField(verbose_name="二维码路径", max_length=100, null=True)
    is_binding = models.BooleanField(verbose_name='是否绑定', default=False)