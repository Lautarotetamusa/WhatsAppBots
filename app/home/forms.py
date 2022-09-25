from django import forms
from django.core.exceptions import ValidationError
from home.models import Campaign, Bot
from utils import spintax

import csv #Para validar el archivo de posts
from io import StringIO

import datetime

class BotForm(forms.ModelForm):
    class Meta():
        model = Bot
        fields = ["phone", "proxy"]

        widgets = {
            "phone": forms.TextInput(attrs={'class': 'form-control'}),
            "proxy": forms.TextInput(attrs={'class': 'form-control'}),
        }

    #Method to validate the data
    def clean(self):

        phone = self.cleaned_data.get("phone")
        proxy = self.cleaned_data.get("proxy")

        #Validar que el numero no este creado ya
        if phone == "":
            self.add_error("phone", "The number cant be empty")

        if Bot.objects.filter(phone=phone).exists():
            self.add_error("phone", "This number is already register")

        #Validar que la sintaxis del proxy este bien
        #ip:port:user:pass
        if proxy != "" and len(proxy.split(":")) != 4:
            self.add_error("proxy", "The proxy sintax is wrong")


        return self.cleaned_data


class CampaignForm(forms.ModelForm):

    response_spintax = forms.CharField(required=False, widget=forms.Textarea(
        attrs={
            'class': 'form-control',
            "rows": 4
        }))

    class Meta():
        model = Campaign
        fields = ['posts', 'spintax', "response_spintax", "msg_per_hour", "rnd_msg", 'start_at', 'end_at', 'rnd_time']

        widgets = {
            "posts":   forms.FileInput(
                attrs={'class': 'form-control'}
            ),
            "spintax": forms.Textarea(
                attrs={
                    'class': 'form-control',
                    "rows": 4
                }
            ),
            "msg_per_hour": forms.TextInput(
                attrs={
                    'class': 'custom-range',
                    'type': 'range',
                    'max': 10
                }
            ),
            "rnd_msg": forms.TextInput(
                attrs={
                    'class': 'custom-range',
                    'type': 'range',
                    'max': 4
                }
            ),
            "start_at":forms.TimeInput(
                format='%hh:%mm',
                attrs={
                    'class': 'form-control',
                    'type': 'time'
                }
            ),
            "end_at":forms.TimeInput(
                format='%H:%M',
                attrs={
                    'class': 'form-control',
                    'type': 'time'
                }
            ),
            "rnd_time": forms.TextInput(
                attrs={
                    'class': 'custom-range',
                    'type': 'range',
                    'max': 60
                }
            )
        }


    #Este metodo se usa para validar la data
    def clean(self):
        #super(PostForm, self).clean()

        #Validar que la sintaxis de  spintax este bien
        spintax_msg = self.cleaned_data.get("spintax")

        if not spintax.validate(spintax_msg):
            #raise ValidationError("The spintax sintax is wrong")
            self.add_error("spintax", "The spintax sintax is wrong")

        #Validar que el archivo sea csv
        posts_file = self.cleaned_data.get("posts")

        if posts_file.name.split(".")[1] == "csv":

            #Validar que los campos seleccionados esten en el archivo
            posts = posts_file.readline().decode('utf-8')
            csv_reader = csv.reader(StringIO(posts), delimiter=',')
            headers = next(csv_reader)

            fields = spintax.get_fields(spintax_msg)
            print(headers)
            print(fields)

            if "phone" not in headers:
                self.add_error("posts", "the file must be contain 'phone' header")

            for field in fields:
                if field not in headers:
                    self.add_error("spintax", "field '%s' is not in file headers" % field)
                    self.add_error("posts", "headers: [%s]" % ', '.join(headers))
                    #raise ValidationError(
                    #    "The field %(field)s is not in file headers",
                    #    params={'field': field}
                    #)
        else:
            #raise ValidationError("The posts file extension must be .csv")
            self.add_error("posts", "The posts file extension must be .csv")

        #Validar que el time_start sea antes que el time_end
        min_time = datetime.time()

        time_start = self.cleaned_data.get("start_at")
        time_end = self.cleaned_data.get("end_at")

        #No está valido que los tiempos tengan una diferencia mayor a X tiempo
        #Convert time to date objects because time cant be substracted
        #dt_max = datetime.datetime.combine(datetime.date.today(), time_end)
        #dt_min = datetime.datetime.combine(datetime.date.today(), time_start)

        if time_start >= time_end:
            #raise ValidationError("The time start must be before end time")
            msg = "The time start must be before end time"
            self.add_error("start_at", "The time start must be before end time")
            self.add_error("end_at", "The time start must be before end time")

        return self.cleaned_data
