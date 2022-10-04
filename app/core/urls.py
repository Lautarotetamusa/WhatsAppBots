from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path('', views.index, name="index"),
    path('new_bot.html', views.new_bot, name='New bot'),
    #path('bot_detail.html', views.bot_detail, name="Bot detail"),
    path('new_campaign.html', views.new_campaign, name="New Campaign"),
    path('close_bot.html', views.close_bot, name="Close bot"),
    path('campaigns.html', views.campaigns, name="Campaigns"),
    path('statistics.html', views.filter_request, name="Statistics"),
    path('messages.html', views.filter_request, name="Messages"),
    path('responses.html', views.filter_request, name="Responses"),
    path('conversations.html', views.filter_request, name="Responses")
]
