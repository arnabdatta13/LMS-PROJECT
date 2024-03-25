# Generated by Django 4.2.1 on 2024-03-18 15:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0059_remove_question_exam_delete_exam'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exam_name', models.CharField(max_length=50)),
                ('total_questions', models.PositiveIntegerField()),
                ('total_marks', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('class_id', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='app.class')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.course')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.subject')),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='exam',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='app.exam'),
        ),
    ]
