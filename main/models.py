from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Student(models.Model):
    user  = models.OneToOneField(User,on_delete=models.CASCADE)
    name  = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    phone = models.IntegerField(default=False)
    budget_total = models.IntegerField(blank=False)
    budget_spent = models.IntegerField(blank=False, default=0)
    preferred_restaurants = models.TextField(null=False)
    preferred_cuisines = models.TextField(null=False)
    not_preferred = models.TextField(null=False)

    def __str__(self):
        return self.name

class Document(models.Model):
    user  = models.ForeignKey(Student,on_delete=models.CASCADE)
    Day_of_name = models.IntegerField(blank=False)
    Time = models.CharField(max_length=300)
    food_item_name = models.CharField(max_length=200)
    # upload_mess_menu = models.FileField(upload_to='uploads/%Y/%m/%d')
