# Generated by Django 3.2.5 on 2021-08-11 19:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_rename_longitute_vendor_longitude'),
    ]

    operations = [
        migrations.RenameField(
            model_name='student',
            old_name='longitute',
            new_name='longitude',
        ),
    ]