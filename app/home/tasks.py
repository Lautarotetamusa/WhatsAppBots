from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery.utils.log import get_task_logger
from home.celery import app
from home import settings

from home.models import Campaign, Bot, Message, Response
from utils.timefunctions import parse_time
from utils import spintax
from datetime import datetime, date, timedelta
import pytz
import random
import time
import csv

from driver.wppdriver import NotLogin

#Logs
logger = get_task_logger(__name__)

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

        times["start_at"] = parse_time(times["start_at"])
        times["end_at"]   = parse_time(times["end_at"])

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

        print("campaign: ", campaign.pk)
        print("start:", times["start_at"])
        print("end:",   times["end_at"])
        print("task id:", task.id)

#Envia un mensaje desde un bot a un numero y guarda los resultados
@shared_task
#send_message(bot, post["phone"], campaign, msg)
def send_message(bot, reciver, campaign, text, max_tries=2):

    print("Sending message to", reciver)

    for _ in range(max_tries):
        message = Message(
            sender = bot,
            campaign = campaign,
            text = text,
            reciver = reciver
        )

        try:
            bot.send(reciver, text)
            print("Sended successfuly")
            message.error = None
            message.consume = bot.consumed()
            break
        except NotLogin:
            print("the session", bot.phone, "is closed")
            message.error = "session closed"
            bot.is_active = False
            bot.save()
            break
        except Exception as e:
            message.error = e
            print("Error sending, retrying", e)


    message.success = (message.error == None)
    message.save()

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
                print("any active bots")
                break

            bot = bots[bot_i%len(bots)]
            bot_i += 1

            campaign.nro_post += 1
            campaign.save()

            if post["phone"] == "":
                print("Phone field is empty")
                print(post)
                continue

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

            #Send the message
            msg = spintax.format(campaign.spintax, post)
            send_message(bot, post["phone"], campaign, msg)

            #Autoresponses
            if campaign.response_spintax != "":
                new_messages = bot.get_messages()

                for message in new_messages:
                    if Message.objects.filter(reciver=message["number"]).count() == 1:
                        print("++++++++++++++++++++++++++++++++++")
                        print("Answer of:", message["number"])
                        print(message["text"])

                        response = Response(
                            sender = message["number"],
                            reciver= bot,
                            text   = message["text"],
                            campaign = campaign
                        )
                        response.save()

                        msg = spintax.spin(campaign.response_spintax)
                        send_message(bot, message["number"], campaign, msg)
                        print("++++++++++++++++++++++++++++++++++")

            bot.close()
            print("----------------------------------")

            #Cuando pasa por todos los numeros
            #Wait for random minutes
            if bot_i%len(bots) == 0:
                print("Waiting...")
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

@app.task()
def test_task():
    logger.info("Starting test task")
    time.sleep(60)
    logger.info("End test task")
