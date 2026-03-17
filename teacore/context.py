from django.utils import timezone
from django.conf import settings

def context(request):
    if hasattr(request, 'session') and not request.session.exists(request.session.session_key):
        request.session.create()

    APP_HOST = settings.APP_HOST
    APP_URL = f"{APP_HOST}{request.path}"

    variables = {

        'HX_BOOSTED': True if 'HTTP_HX_BOOSTED' in request.META else False,
        'HX_REQUEST': True if 'HTTP_HX_REQUEST' in request.META else False,
        'MEDIA_URL': settings.MEDIA_URL,
        'STATIC_URL': settings.STATIC_URL,
        'DATETIME': timezone.now(),

        'APP_HOST': APP_HOST,
        'APP_URL': APP_URL,

        'THEME': request.META['THEME'] if 'THEME' in request.META and settings.THEME == "user" else settings.THEME,
        'DARKMODE': request.META['DARKMODE'] if 'DARKMODE' in request.META else settings.DARKMODE,
        'NEXT': request.GET.get("next", "")
    }
    
    variables.update({
        key: getattr(settings, key) 
        for key in dir(settings) 
        if key.startswith("APP_")
    })
    
    variables.update({
        key: getattr(settings, key) 
        for key in dir(settings) 
        if key.startswith("CMS_")
    })
    
    variables.update({
        key: getattr(settings, key) 
        for key in dir(settings) 
        if key.startswith("META_")
    })

    variables.update({
        key: getattr(settings, key) 
        for key in dir(settings) 
        if key.startswith("TRACK_")
    })

    variables.update({
        key: getattr(settings, key) 
        for key in dir(settings) 
        if key.startswith("SOCIAL_")
    })

    variables.update({
        key: getattr(settings, key) 
        for key in dir(settings) 
        if key.startswith("AUTH_")
    })
    
    return variables