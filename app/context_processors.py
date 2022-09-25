from django.conf import settings

#Pasar las variables configuradas en el settings a los templates

def cfg_assets_root(request):
    return { 'ASSETS_ROOT' : settings.ASSETS_ROOT }
