from django.db import models

from driver import wppdriver

from core import settings
from shutil import rmtree #Eliminar las carpetas de session
import datetime

class Bot(models.Model, wppdriver.WhatsAppDriver):
    phone = models.CharField(max_length=15, primary_key=True)
    proxy = models.CharField(max_length=60, blank=True)
    login_at = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=False)

    def path(self):
        return f"{settings.SESSIONS}/{self.phone}"

    def time_left(self):
        active_days = 14
        if self.is_active:
            time_end = self.login_at + datetime.timedelta(days=active_days)

            left = time_end.replace(microsecond=0) - datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
            return left

    def close_session(self):
        print("deleting session folder", self.path())
        try:
            rmtree(self.path())
        except FileNotFoundError:
            print("session is already closed")
        self.is_active = False
        self.save()

class Campaign(models.Model):
    RUNNING = 0
    PENDING = 1
    FINISHED = 2
    STATUS_CHOICES = (
        (RUNNING, 'Running'),
        (PENDING, 'Pending'),
        (FINISHED, 'Finished')
    )

    posts = models.FileField(upload_to='posts', default=None)
    nro_post = models.IntegerField(default=0)
    status = models.IntegerField(default=1, choices=STATUS_CHOICES)
    task_id = models.CharField(max_length=40, default="")

    spintax = models.CharField(max_length=500)
    response_spintax = models.CharField(blank=True, null=True, max_length=500) #No depende del post

    msg_per_hour = models.IntegerField(null=True)
    rnd_msg = models.IntegerField(default=0)          #Cantidad aleatoria de mensajes enviados por hora además de los seteados en msg_hour

    start_at = models.TimeField()
    end_at = models.TimeField()
    rnd_time = models.IntegerField(default=0)         #Tiempo aleatorio en el que comienza y terminan la campaña en un dia

class Conversation(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    client = models.CharField(max_length=15)
    start  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bot.phone} => {self.client}"

class Message(models.Model):
    SENDED  = 0
    RECIVED = 1
    STATUS_CHOICES = (
        (SENDED, 'Sended'),
        (RECIVED, 'Recived')
    )
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    time = models.DateTimeField(auto_now_add=True)
    type = models.IntegerField(choices=STATUS_CHOICES)

    error = models.CharField(max_length=100, null=True)
    def success(self):
        return self.error == None

    def __str__(self):
        return f"{self.text}"
