# Generated by Django 3.2.5 on 2021-08-12 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_rename_longitute_student_longitude'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='preferred_vendors',
            field=models.TextField(null=True),
        ),
    ]
