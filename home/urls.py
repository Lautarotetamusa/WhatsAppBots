"""home URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path('', views.index, name="index"),
    path('bots.html', views.bots, name='home'),
    path('new_bot.html', views.new_bot, name='New bot'),
    path('scan_qr.html', views.default, name="Scan QR"),
    path('bot_detail.html', views.bot_detail, name="Bot detail"),
    path('new_campaign.html', views.new_campaign, name="Bot detail")
]
