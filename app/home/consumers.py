import json
import time
from datetime import datetime

from channels.consumer import SyncConsumer
from channels.generic.websocket import JsonWebsocketConsumer

from home.models import Bot

class CreateBotConsumer(JsonWebsocketConsumer):

    def connect_json(self):
        self.accept()

    #Cuando recibe un mensaje desde la view
    #Crea un nuevo Bot
    def receive_json(self, content):
        if content["status"] == "start":
            print("phone", content["phone"])
            print("proxy", content["proxy"])


            bot = Bot.objects.get(phone=content["phone"])
            #Si no existe, creamos uno nuevo
            if not bot:
                print("bot not registered, creating new")
                bot = Bot(
                    phone = content["phone"],
                    proxy = content["proxy"]
                )
            else:
                print("bot already registered, revalidating")

            try:
                bot.open()
                bot.main_page()
                qrdata = bot.generate_qr()
                print(type(qrdata))
                self.send_json({
                    "msg": "qrgenerated",
                    "data": qrdata
                })

                bot.is_login()

                bot.login_at = datetime.now()
                bot.is_active = True
                bot.save()

                self.send_json({"msg": "login", "status": True})
            except Exception as e:
                error  = e.__class__.__name__ + "\n"
                error += str(e) + "\n"
                self.send_json({"msg": "error", "exception": error})
