# Generated by Django 4.2.1 on 2023-10-19 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_student_activity'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher_notification',
            name='status',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
