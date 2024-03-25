# Generated by Django 4.2.1 on 2024-03-12 13:37

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0035_remove_course_created_at_remove_course_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='class1',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.class'),
        ),
        migrations.AddField(
            model_name='course',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='course',
            name='name',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='course',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
