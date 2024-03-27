# Generated by Django 4.2.7 on 2024-03-24 14:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0011_announcement'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='content',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='announcement',
            name='date_posted',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='announcement',
            name='title',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
