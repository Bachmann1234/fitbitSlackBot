from django.contrib.auth.models import User
from django.db import models


class Token(models.Model):
    user = models.ForeignKey(User)
    fitbit_id = models.CharField(max_length=50)
    refresh_token = models.CharField(max_length=120)
