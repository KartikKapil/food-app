from django.db import models

# Create your models here.

class Customer(models.Model):
    name  = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    phone = models.IntegerField(default=False)
    budget = models.IntegerField(blank=False)
    preferred_restuarnt = models.TextField(null=False)
    preferred_cusine = models.TextField(null=False)
    upload_mess_menu = models.FileField(upload_to='uploads/%Y/%m/%d')

    def __str__(self):
        return self.name