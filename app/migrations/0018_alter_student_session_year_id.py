# Generated by Django 4.2 on 2023-09-24 14:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_alter_subject_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='session_year_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.session_year'),
        ),
    ]
