# Generated by Django 5.0.6 on 2024-11-08 18:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_points'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schoolexamstudentresult',
            name='student_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='studentresult', to='app.student'),
        ),
    ]