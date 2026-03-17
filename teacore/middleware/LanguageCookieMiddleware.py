from django.conf import settings
from django.utils import translation

from teacore.models import Lang


class LanguageCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language_code_cookie = request.COOKIES.get("lang")
        language_code_param = request.GET.get("lang")
        lang_array = list(
            Lang.objects.filter(is_enabled=True).values_list("code", flat=True)
        )

        if language_code_param and language_code_param in lang_array:
            translation.activate(language_code_param)
        elif language_code_cookie and language_code_cookie in lang_array:
            translation.activate(language_code_cookie)

        response = self.get_response(request)
        return response
