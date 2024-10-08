# Generated by Django 5.0.6 on 2024-06-14 07:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_live_exam_mcq_result_live_exam_written_result'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='liveexamstudentwrittenanswer',
            name='answer_image',
        ),
        migrations.CreateModel(
            name='LiveExamStudentWrittenAnswerImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='media/answers/')),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='app.liveexamstudentwrittenanswer')),
            ],
        ),
    ]
