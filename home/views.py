from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django import template

from home.models import Bot, Campaign, Message
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

#bots list
def index(request):
    bot_list = Bot.objects.all()

    #Calcular el tiempo que queda hasta que se cierren las sesiones
    for bot in bot_list:
        if bot.is_active:
            time_end = bot.login_at + datetime.timedelta(days=14)

            bot.time_left = time_end - datetime.datetime.now(datetime.timezone.utc) # as timedelta

    return render(request, "home/index.html", {'bot_list': bot_list})

#campaign list
def campaigns(request):
    campaigns = Campaign.objects.all()
    return render(request, "home/campaigns.html", {"campaigns": campaigns})

def statistics(request):
    messages = Message.objects.all()

    if request.GET:
        if "campaign_id" in request.GET:
            id = request.GET["campaign_id"]
            if id != "": #Si el id es 0 estamos seleccionando todas las campañas
                messages = messages.filter(campaign=id)

        if "bot_phone" in request.GET:
            bot_phone = request.GET["bot_phone"]
            if bot_phone != "":            #Si el phone es 0 estamos seleccionando todas los bots
                messages = messages.filter(sender=bot_phone)

        if "date_input" in request.GET and request.GET["date_input"] != "":
            date = datetime.datetime.strptime(request.GET["date_input"], "%Y-%m-%d")
            messages = messages.filter(sended_at__day = date.day)

    chart = [
        {"label": "errors", "value": messages.filter(success=False).count()},
        {"label": "success","value": messages.filter(success=True).count()}
    ]

    context = {
        "data": chart,
        "form": request.GET,
        "campaigns": Campaign.objects.all().values_list("pk", flat=True),
        "bots": Bot.objects.all().values_list("phone", flat=True)
    }
    return render(request, "home/statistics.html", context)

def messages(request):
    messages = Message.objects.all()

    if request.GET:
        if "campaign_id" in request.GET:
            id = request.GET["campaign_id"]
            if id != "": #Si el id es 0 estamos seleccionando todas las campañas
                messages = messages.filter(campaign=id)

        if "bot_phone" in request.GET:
            bot_phone = request.GET["bot_phone"]
            if bot_phone != "":            #Si el phone es 0 estamos seleccionando todas los bots
                messages = messages.filter(sender=bot_phone)

        if "date_input" in request.GET and request.GET["date_input"] != "":
            date = datetime.datetime.strptime(request.GET["date_input"], "%Y-%m-%d")
            messages = messages.filter(sended_at__day = date.day)

    context = {
        "messages": messages,
        "total": messages.count(),
        "form": request.GET,
        "campaigns": Campaign.objects.all().values_list("pk", flat=True),
        "bots": Bot.objects.all().values_list("phone", flat=True),
    }
    return render(request, "home/messages.html", context)

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
    elif "bot_phone" in request.GET:
            bot = Bot.objects.get(phone=request.GET["bot_phone"])
            form = BotForm({
                "phone":bot.phone,
                "proxy":bot.proxy
            })
    else:
        form = BotForm()

    return render(request, 'home/new_bot.html', {"form": form, "errors": has_error})

def bot_detail(request):
    #Find the requested phone
    find = Bot.objects.filter(phone=request.GET["phone"])

    context = {"find": len(find) > 0}

    if len(find) > 0:
        context["bot"] = find[0]

    template = loader.get_template()
    return render('home/bot_detail.html', context)
