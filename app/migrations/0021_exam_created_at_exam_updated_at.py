# Generated by Django 4.2.1 on 2023-09-28 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_star_student'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='exam',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
