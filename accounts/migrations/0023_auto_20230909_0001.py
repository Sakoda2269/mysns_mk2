# Generated by Django 3.0.2 on 2023-09-08 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0022_auto_20230908_2328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(max_length=254, null=True, unique=True, verbose_name='email address'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='usertag',
            field=models.CharField(max_length=16, null=True, unique=True, verbose_name='usertag'),
        ),
    ]
