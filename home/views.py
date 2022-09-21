from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django import template

from home.models import Bot, Campaign
from home.forms  import CampaignForm, BotForm
from utils import csvfunctions

from time import sleep
import datetime                 #Para poder calcular la fecha de cierre de sesion
from threading import Thread    #Para poder crear la sesion
from home import settings

def default(request):

    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    context = {}
    try:
        load_template = request.path.split('/')[-1]

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
        return render(request, 'home/page-404.html')
    except:
        return render(request, 'home/page-500.html')

def index(request):
    bot_list = Bot.objects.all()

    context = {'segment': 'index', 'bot_list': bot_list}

    #Calcular el tiempo que queda hasta que se cierren las sesiones
    for bot in bot_list:
        if bot.is_active:
            time_end = bot.login_at + datetime.timedelta(days=14)

            delta = time_end - datetime.datetime.now(datetime.timezone.utc) # as timedelta
            print(delta)

            bot.time_left = delta

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

def new_campaign(request):
    if request.method == 'POST':
        form_data = request.POST

        form = CampaignForm(request.POST, request.FILES)

        if form.is_valid():
            print("form valid")

            campaign = Campaign(
                posts = request.FILES["posts"],
                spintax = form_data["spintax"],
                response_spintax = form_data["response_spintax"],
                start_at = form_data["start_at"],
                end_at = form_data["end_at"],
                rnd_time = int(form_data["rnd_time"]),
                msg_per_hour = int(form_data["msg_per_hour"]),
                rnd_msg = int(form_data["rnd_msg"])
            )

            campaign.save()

            #Lo guardamos antes porque sino el archivo no se sube
            campaign.posts = csvfunctions.parse_phones(campaign.posts.path)
            campaign.save()
        else:
            for field in form.errors:
                form[field].field.widget.attrs['style'] = 'border: 1px solid var(--danger);'
            print("form invalid")

    else:
        form = CampaignForm()

    return render(request, 'home/new_campaign.html', {"form": form})

def new_bot(request):

    has_error = ""
    if request.method == "POST":
        form = BotForm(request.POST)

        if form.is_valid():
            print("form valid")
            has_error = "false"
        else:
            for field in form.errors:
                form[field].field.widget.attrs['style'] = 'border: 1px solid var(--danger);'
            has_error = "true"
    else:
        form = BotForm()

    return render(request, 'home/new_bot.html', {"form": form, "errors": has_error})

def bot_detail(request):
    #Find the requested phone
    find = Bot.objects.filter(phone=request.GET["phone"])

    context = {"find": len(find) > 0}

    if len(find) > 0:
        context["bot"] = find[0]

    template = loader.get_template('home/bot_detail.html')
    return HttpResponse(template.render(context, request))

def bots(request):
    bot_list = Bot.objects.all()

    context = {'segment': 'bots', 'bot_list': bot_list}

    html_template = loader.get_template('home/bots.html')
    return HttpResponse(html_template.render(context, request))
