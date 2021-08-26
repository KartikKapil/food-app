import csv
import json
import os
from math import asin, cos, radians, sin, sqrt

import requests

from .models import Menu, Restaurant, Student, User, Vendor


def distance(lat1, lat2, lon1, lon2):
    """TO FIND THE DISTANCE BETWEEN TWO GIVEN POSITIONAL CORDINATES"""

    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2

    c = 2 * asin(sqrt(a))

    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371

    # calculate the result
    return(c * r)

def handle_uploaded_file(f, username):
    """TO CHECK READ AND INITIATE OBJECTS OF MENU CLASS WHILE SIMINTALOUS LIKING THEM TO STUDENT OBJECTS """

    fields = []
    objects = []
    days = {"sunday": 0, "monday": 1, "tuesday": 2, "wednesday": 3, "thursday": 4, "friday": 5, "saturday": 6}

    with open('temp_menu.csv', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    with open('temp_menu.csv', 'r') as destination:
        csvreader = csv.reader(destination)
        next(csvreader)
        for j in range(6):
            fields = next(csvreader)
            fields[0] = days[fields[0].lower()]
            objects.append(fields)

    os.remove('temp_menu.csv')

    time_of_the_day = ['breakfast', 'lunch', 'dinner']
    user = User.objects.get(username=username)
    student_name = user.student.name
    student = Student.objects.get(name=student_name)

    for items in objects:
        i = 1
        for time in time_of_the_day:
            newDoc = Menu(student=student, day=items[0], time=time, dishes=items[i])
            i = i+1
            newDoc.save()


def get_restaurants(ids_str, username):
    ids = ids_str.split(",")
    headers = {
        'accept': 'application/json',
        'user-key': '28c7fdb103232548b1503df6df9b4520',
    }

    rests = []
    for res_id in ids:
        response = requests.get(
            'https://developers.zomato.com/api/v2.1/restaurant?res_id=' + str(res_id),
            headers=headers)
        data = response.json()

        rests.append({"name": data["name"], "price": data["average_cost_for_two"]
                     // 2, "address": data["location"]["address"]})

    user = User.objects.get(username=username)
    student = user.student

    for rest in rests:
        new_rest = Restaurant(student=student, name=rest["name"], price=rest["price"], address=rest["address"])
        new_rest.save()

#  get_restaurants('307374,307113')

def Distance_between_user_and_vendors(latitude_user,longitute_user,raidus_of_action):
    """TO GIVE THE LIST OF NEAREST RESTUTARNTS OF A GIVEN USER"""

    latitude_user = float(latitude_user)
    longitute_user = float(longitute_user)
    Vendors = Vendor.objects.all()
    Nearby_vendors = []
    for vendors in Vendors:
        vendor_latitude = vendors.latitude
        vendor_longitute = vendors.longitude
        if(distance(latitude_user,vendor_latitude,longitute_user,vendor_longitute)<=raidus_of_action):
            Nearby_vendors.append({"id": vendors.user.username, "name": vendors.name})

    Vendor_Names = {"vendors":Nearby_vendors}
    return Vendor_Names

