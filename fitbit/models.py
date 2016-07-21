from django.contrib.auth.models import User
from django.db import models


class Token(models.Model):
    fitbit_id = models.CharField(max_length=50)
    refresh_token = models.CharField(max_length=120)

    def __repr__(self):
        return '<Token %s>' % self.fitbit_id

    def __str__(self):
        return self.fitbit_id
