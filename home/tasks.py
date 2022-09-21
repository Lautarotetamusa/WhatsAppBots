from __future__ import absolute_import, unicode_literals

from celery import shared_task
from home.celery import app
from home import settings

from home.models import Campaign, Bot, Message
from utils.timefunctions import parse_time
from utils import spintax
from datetime import datetime, date, timedelta
import pytz
import random
import time
import csv

from driver.wppdriver import NotLogin


#Esta funcion se ejecuta todos los días a las 00:00hs
#Se encarga de buscar que campañas necesitan ejecucion y llamar
#a las funciones que envian los mensajes en las horas determinadas.
@shared_task
def manage_campaign():

    #Si hay alguna campaña RUNNING elegimos las primera
    #Si no hay ninguna elegimos la primera PENDING
    #Si no hay ninguna de las dos, no hacemos nada
    campaign = None
    statuses = [Campaign.PENDING, Campaign.RUNNING]
    for status in statuses:
        for c in Campaign.objects.filter(status=status):
            campaign = c
            break

    if campaign != None:
        campaign.status = Campaign.RUNNING

        #Setear las horas aleatorias
        times = {"start_at": 0, "end_at": 0}
        for time in times:
            timeobj =  getattr(campaign, time)

            rnd_minutes = 61
            while rnd_minutes > 60 or rnd_minutes < 0:
                rnd_minutes = random.randint(
                    timeobj.minute - campaign.rnd_time,
                    timeobj.minute + campaign.rnd_time
                )

            times[time] = timeobj.replace(minute=rnd_minutes)

        #times["start_at"] = parse_time(datetime.now().time().replace(hour=13, minute=28))
        #times["end_at"]   = parse_time(datetime.now().time().replace(hour=13, minute=32))

        task = send_messages.apply_async(
            eta = times["start_at"],
            args = [campaign.pk]
        )

        end_task.apply_async(
            eta = times["end_at"],
            args = [task.id]
        )

        campaign.task_id = task.id
        campaign.save()

        print("start:", times["start_at"])
        print("end:",   times["end_at"])
        print("task id:", task.id)

#Envia todos los mensajes en un dia
@shared_task
def send_messages(campaign_pk):
    campaign = Campaign.objects.get(pk=campaign_pk)

    #Calcular cada cuanto tiempo se tiene q enviar mensajes
    msg_per_hour = campaign.msg_per_hour + random.randint(-campaign.rnd_msg, campaign.rnd_msg)
    msg_period = 60.0 / msg_per_hour

    with campaign.posts.open('r') as f:
        posts = csv.DictReader(f)

        #Ir hasta la linea en la que nos quedamos
        if campaign.nro_post == 0:
            next(posts)
        for _ in range(campaign.nro_post):
            next(posts)
        print(campaign.nro_post)

        bot_i = 0

        #Recorrer todos los posts
        for post in posts:
            bots = Bot.objects.filter(is_active=True)

            if len(bots) == 0:
                break

            bot = bots[bot_i%len(bots)]
            bot_i += 1

            campaign.nro_post += 1
            campaign.save()

            print("----------------------------------")
            print(bot.phone)
            print(bot.proxy)

            #Open the session
            try:
                bot.open()
                print("session open")
            except Exception as e:
                print("Driver cant load")
                print(e.__class__.__name__)
                print(e)
                continue

            if post["phone"] == "":
                print("Phone field is empty")
                continue

            print("sending message to", post["phone"])

            #Send the message
            msg = spintax.format(campaign.spintax, post)

            #Save the Message objects
            message = Message(
                sender = bot,
                campaign = campaign,
                text = msg,
                reciver = post["phone"],
                consume = bot.consumed()
            )

            try:
                bot.send(post["phone"], msg)
            except NotLogin:
                print("the session", bot.phone, "is closed")
                message.error = "session closed"
                bot.is_active = False
                bot.save()
            except Exception as e:
                print(e)
                message.error = e

            message.success = (message.error == None)

            message.save()
            bot.close()
            print("----------------------------------")

            #Wait for random minutes
            #Cuando pasa por todos los numeros
            if bot_i%len(bots) == 0:
                print("Waiting...")

                ####################
                ########SACAR######
                #msg_period=0.3
                ####################
                time.sleep(60*msg_period)



    print("Campaign finished")
    campaign.status = campaign.FINISHED
    campaign.save()

@shared_task
def end_task(task_id):
    print(task_id)
    app.control.revoke(task_id, terminate=True)

@shared_task
def terminate_running_campaign():
    campaign = Campaign.objects.filter(status=Campaign.RUNNING)
    if campaign:
        app.control.revoke(campaign[0].task_id, terminate=True)
    else:
        print("No running campaigns")
