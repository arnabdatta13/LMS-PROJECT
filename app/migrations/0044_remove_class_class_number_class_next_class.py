# Generated by Django 4.2.1 on 2024-03-18 02:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0043_class_class_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='class',
            name='class_number',
        ),
        migrations.AddField(
            model_name='class',
            name='next_class',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='previous_class', to='app.class'),
        ),
    ]
