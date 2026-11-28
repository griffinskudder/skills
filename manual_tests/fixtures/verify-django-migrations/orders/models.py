from django.db import models


class Order(models.Model):
    order_number = models.CharField(max_length=16, unique=True)
    external_reference = models.CharField(max_length=20, unique=True)
