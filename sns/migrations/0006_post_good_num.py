# Generated by Django 3.0.2 on 2023-08-14 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sns', '0005_auto_20230814_1737'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='good_num',
            field=models.IntegerField(default=0),
        ),
    ]
