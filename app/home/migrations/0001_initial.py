# Generated by Django 4.1 on 2022-09-20 20:09

from django.db import migrations, models
import django.db.models.deletion
import driver.wppdriver


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bot',
            fields=[
                ('phone', models.CharField(max_length=15, primary_key=True, serialize=False)),
                ('proxy', models.CharField(blank=True, max_length=60)),
                ('login_at', models.DateTimeField(null=True)),
                ('is_active', models.BooleanField(default=False)),
            ],
            bases=(models.Model, driver.wppdriver.WhatsAppDriver),
        ),
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('posts', models.FileField(default=None, upload_to='posts')),
                ('nro_post', models.IntegerField(default=0)),
                ('status', models.IntegerField(choices=[(0, 'Running'), (1, 'Pending'), (2, 'Finished')], default=1)),
                ('task_id', models.CharField(default='', max_length=40)),
                ('spintax', models.CharField(max_length=500)),
                ('response_spintax', models.CharField(blank=True, max_length=500, null=True)),
                ('msg_per_hour', models.IntegerField(null=True)),
                ('rnd_msg', models.IntegerField(default=0)),
                ('start_at', models.TimeField()),
                ('end_at', models.TimeField()),
                ('rnd_time', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=500)),
                ('reciver', models.CharField(max_length=15)),
                ('sended_at', models.DateTimeField(auto_now_add=True)),
                ('consume', models.FloatField(null=True)),
                ('success', models.BooleanField(default=False)),
                ('error', models.CharField(default=None, max_length=100)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.campaign')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.bot')),
            ],
        ),
    ]