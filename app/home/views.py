from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django import template
from django.contrib import messages

from home.models import Bot, Campaign, Message, Response
from home.forms  import CampaignForm, BotForm
from utils import csvfunctions
from home import settings

import datetime                 #Para poder calcular la fecha de cierre de sesion

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
    return render(request, "home/index.html", {'bot_list': Bot.objects.all()})
def campaigns(request):
    return render(request, "home/campaigns.html", {"campaigns": Campaign.objects.all()})

def filter_request(request):
    messages  = Message.objects.all()
    responses = Response.objects.all()
    template = request.path.split('/')[-1]

    if "campaign_id" in request.GET:
        id = request.GET["campaign_id"]
        if id != "": #Si el id es 0 estamos seleccionando todas las campañas
            messages  = messages.filter(campaign=id)
            responses = responses.filter(campaign=id)

    if "bot_phone" in request.GET:
        bot_phone = request.GET["bot_phone"]
        if bot_phone != "":            #Si el phone es 0 estamos seleccionando todas los bots
            messages  = messages.filter(sender=bot_phone)
            responses = responses.filter(reciver=bot_phone)

    if "date_input" in request.GET and request.GET["date_input"] != "":
        date = datetime.datetime.strptime(request.GET["date_input"], "%Y-%m-%d")
        messages  = messages.filter(sended_at__day=date.day)
        responses = responses.filter(sended_at__day=date.day)

    context = {
        "form": request.GET,
        "campaigns": Campaign.objects.all().values_list("pk", flat=True),
        "bots": Bot.objects.all().values_list("phone", flat=True)
    }

    if "statistics" in template:
        context["charts"] = {
            "error": {
                "labels": ["errors", "success"],
                "values": [messages.filter(success=False).count(), messages.filter(success=True).count()]
            },
            "response": {
                "labels": ["not responded", "responded"],
                "values": [messages.count()-responses.count(), responses.count()]
            }
        }
    elif "message" in template:
        context["messages"]  = messages
        context["responses"] = responses
    elif "conversation" in template:
        if "client" in request.GET:
            client = request.GET["client"]
            messages   = messages.filter(reciver=client)
            responses  = responses.filter(sender=client)

            r = 0
            conversation = []
            for m in range(len(messages)):
                res = None
                if r in range(len(responses)):
                    res = responses[r].text
                conversation.append({
                    "msg": messages[m].text,
                    "res": res
                })
                r += 1

            context["conversation"] = conversation

    return render(request, "home/"+template, context)

def new_campaign(request):

    message = None
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
            campaign.posts = csvfunctions.parse_phones(campaign.posts)
            campaign.save()

            message = "Campaign created successfuly"
        else:
            for field in form.errors:
                form[field].field.widget.attrs['style'] = 'border: 1px solid var(--danger);'
            print("form invalid")
    else:
        form = CampaignForm()

    return render(request, 'home/new_campaign.html', {"form": form, "message":message})
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
    elif "bot_phone" in request.GET:
            bot = Bot.objects.get(phone=request.GET["bot_phone"])
            form = BotForm({
                "phone":bot.phone,
                "proxy":bot.proxy
            })
    else:
        form = BotForm()

    return render(request, 'home/new_bot.html', {"form": form, "errors": has_error})

#####
def close_bot(request):
    if "bot_phone" in request.GET:
        bot = Bot.objects.get(phone=request.GET["bot_phone"])
        if bot:
            bot.close_session()
            return render(request, "home/bot_detail.html", {"find":True, "bot":bot})

    return render(request, "home/bot_detail.html", {"find":False})
def bot_detail(request):
    #Find the requested phone
    find = Bot.objects.filter(phone=request.GET["phone"])

    context = {"find": len(find) > 0}

    if len(find) > 0:
        context["bot"] = find[0]

    template = loader.get_template()
    return render('home/bot_detail.html', context)
