# Generated by Django 3.0.2 on 2023-08-27 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sns', '0007_auto_20230817_0148'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='mode',
            field=models.IntegerField(default=0),
        ),
    ]
