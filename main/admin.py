from django.contrib import admin

from .models import Menu, Restaurant, Student, Transcations, Vendor

admin.site.register(Student)
admin.site.register(Menu)
admin.site.register(Vendor)
admin.site.register(Transcations)
admin.site.register(Restaurant)
