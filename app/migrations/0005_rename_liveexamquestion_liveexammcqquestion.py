# Generated by Django 5.0.6 on 2024-06-06 08:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_onlineliveclass_course'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='LiveExamQuestion',
            new_name='LiveExamMCQQuestion',
        ),
    ]
