from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path('', views.index, name="index"),
    path('new_bot.html', views.new_bot, name='New bot'),
    #path('bot_detail.html', views.bot_detail, name="Bot detail"),
    path('new_campaign.html', views.new_campaign, name="New Campaign"),
    path('statistics.html', views.statistics, name="Statistics"),
    path('campaigns.html', views.campaigns, name="Campaigns"),
    path('messages.html', views.messages, name="Messages")
]
