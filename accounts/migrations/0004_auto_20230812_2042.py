# Generated by Django 3.0.2 on 2023-08-12 11:42

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20230812_2025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='id',
            field=models.UUIDField(default=uuid.UUID('ab2b54b4-7dac-4c40-9fff-b22aceb5d468'), editable=False, primary_key=True, serialize=False),
        ),
    ]
