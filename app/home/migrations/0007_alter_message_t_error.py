# Generated by Django 4.1 on 2022-10-01 00:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_conversation_message_t'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message_t',
            name='error',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
