# Generated by Django 3.0.2 on 2023-08-27 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_auto_20230827_1950'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='usertag',
            field=models.CharField(default='Q03XDIpxmVhbEtZE', max_length=16, unique=True, verbose_name='usertag'),
        ),
    ]