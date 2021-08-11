from django.contrib import admin

from .models import Menu, Student, Vendor, Transcations, Restaurant

admin.site.register(Student)
admin.site.register(Menu)
admin.site.register(Vendor)
admin.site.register(Transcations)
admin.site.register(Restaurant)
# Register your models here.
