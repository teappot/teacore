from django.conf import settings

class ThemeCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        theme_cookie = request.COOKIES.get('theme')
        theme_param = request.GET.get('theme')
        themes = [
            "none",
            "cerulean",
            "cosmo",
            "cyborg",
            "darkly",
            "flatly",
            "journal",
            "litera",
            "lumen",
            "materia",
            "minty",
            "morph",
            "pulse",
            "quartz",
            "sandstone",
            "simplex",
            "sketchy",
            "slate",
            "solar",
            "spacelab",
            "superhero",
            "united",
            "vapor",
            "yeti",
            "zephyr"
        ]

        darkmode_cookie = request.COOKIES.get('darkmode')
        darkmode_param = request.GET.get('darkmode')
        darkmodes = [
            "dark",
            "light",
            "auto"
        ]
        
        if settings.THEME == "user":
            if theme_cookie and theme_cookie in themes:
                request.META['THEME'] = theme_cookie
            elif theme_param and theme_param in themes:
                request.META['THEME'] = theme_param
        else:
            request.META['THEME'] = settings.THEME
        
        if settings.DARKMODE == "auto":
            if darkmode_cookie and darkmode_cookie in darkmodes:
                request.META['DARKMODE'] = darkmode_cookie
            elif darkmode_param and darkmode_param in darkmodes:
                request.META['DARKMODE'] = darkmode_param
        else:   
            request.META['DARKMODE'] = settings.DARKMODE

        response = self.get_response(request)
        return response

