# Generated by Django 4.2.7 on 2024-03-22 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0008_alter_student_sem'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseenrollment',
            name='sem',
            field=models.IntegerField(default=1),
        ),
    ]
