import threading
import time
import datetime
import csv
import random

#from home.models import Bot

class CampaignManager(threading.Thread):
    def __init__(self):
        print("init")
        print(self.posts)

    def start(self):
        super().__init__()
        super().start()
        self.status = self.RUNNING
        self.save()

    def run(self):
        print("another thread")

        now = datetime.datetime.now().time()

        #test end_at dentro de 5 segundos
        self.end_at = datetime.time(now.hour, now.minute, now.second + 5)
        print("now", now)
        print("end", self.end_at)

        #dt_max = datetime.datetime.combine(datetime.date.today(), self.start_at)
        #dt_min = datetime.datetime.combine(datetime.date.today(), self.end_at)

        #print(self.start_at)
        #rnd_start = random.randint()
        #rnd_end   = random.randint()

        with self.posts.open('r') as f:
            posts = csv.reader(f)
            headers = next(posts)

            #test para ir al final del archivo
            for i in range(997):
                next(posts)

            while self.status == self.RUNNING:
                if self.start_at <= now <= self.end_at:
                    try:
                        post = next(posts)



                        time.sleep(1)
                    except StopIteration:
                        print("Campaign finished")
                        self.status = self.FINISHED

                now = datetime.datetime.now().time()

    def send_message(post, bot):
        print("a")
