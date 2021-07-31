from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Student(models.Model):
    user  = models.ForeignKey(User,on_delete=models.CASCADE)
    name  = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    phone = models.IntegerField(default=False)
    budget = models.IntegerField(blank=False)
    preferred_restaurants = models.TextField(null=False)
    preferred_cuisines = models.TextField(null=False)
    not_preferred = models.TextField(null=False)

    def __str__(self):
        return self.name

class Document(models.Model):
    upload_mess_menu = models.FileField(upload_to='uploads/%Y/%m/%d')
