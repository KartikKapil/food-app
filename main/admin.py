from django.contrib import admin

from .models import Document, Student

admin.site.register(Student)
admin.site.register(Document)
# Register your models here.
