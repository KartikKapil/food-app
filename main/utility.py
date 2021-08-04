import csv
import os

import requests

from .models import Document, Restaurant, Student, User


def handle_uploaded_file(f, username):
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
            newDoc = Document(student=student, day=items[0], time=time, dishes=items[i])
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
