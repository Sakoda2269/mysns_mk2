# Generated by Django 3.0.2 on 2023-08-13 13:04

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('sns', '0003_auto_20230812_2053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='id',
            field=models.UUIDField(default=uuid.UUID('81842a23-bb8a-405b-8c0a-216b6166cf52'), editable=False, primary_key=True, serialize=False),
        ),
    ]
