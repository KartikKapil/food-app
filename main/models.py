from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    phone = models.IntegerField(default=False)
    budget_total = models.IntegerField(blank=False)
    budget_spent = models.IntegerField(blank=False, default=0)
    preferred_restaurants = models.TextField(null=False)
    preferred_cuisines = models.TextField(null=False)
    not_preferred = models.TextField(null=False)
    longitute = models.FloatField(null=False)
    latitude = models.FloatField(null=False)

    def __str__(self):
        return self.name


class Menu(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    day = models.IntegerField(blank=False)
    time = models.CharField(max_length=20)
    dishes = models.CharField(max_length=200)


class Restaurant(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    price = models.IntegerField(blank=False)


class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    phone = models.IntegerField(default=False)
    price = models.IntegerField(default=False)
    longitude = models.FloatField(null=False)
    latitude = models.FloatField(null=False)

class Transcations(models.Model):
    FROM  = models.ForeignKey(User, related_name='FROM',on_delete=models.CASCADE)
    TO = models.ForeignKey(User, related_name='TO',on_delete=models.CASCADE)
    AMOUNT = models.FloatField(blank=False)
    DATE_TIME = models.DateTimeField(auto_now=True)
