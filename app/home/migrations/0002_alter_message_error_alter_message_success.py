# Generated by Django 4.1 on 2022-09-20 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='error',
            field=models.CharField(default=None, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='success',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
