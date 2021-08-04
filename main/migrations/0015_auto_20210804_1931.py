# Generated by Django 3.2.5 on 2021-08-04 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_alter_student_budget_spent'),
    ]

    operations = [
        migrations.RenameField(
            model_name='document',
            old_name='Day_of_name',
            new_name='day',
        ),
        migrations.RenameField(
            model_name='document',
            old_name='food_item_name',
            new_name='dishes',
        ),
        migrations.RenameField(
            model_name='document',
            old_name='user',
            new_name='student',
        ),
        migrations.RemoveField(
            model_name='document',
            name='Time',
        ),
        migrations.AddField(
            model_name='document',
            name='time',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]