# Generated by Django 4.1 on 2022-10-01 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0010_conversation_start'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='start',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
