from django import template
from teacore.models import Lang
from django.conf import settings

register = template.Library()

@register.inclusion_tag('teacore/customtags/selector-lang.html')
def selector_lang():
    languages = Lang.objects.filter(is_enabled=True)
    
    return { 
        'languages': languages
    }

@register.inclusion_tag('teacore/customtags/selector-theme.html')
def selector_theme(darkmode, theme=None):

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

    return {
        'SETTINGS_THEME': settings.THEME,
        'THEME': theme,
        'SETTINGS_DARKMODE': settings.DARKMODE,
        'DARKMODE': darkmode,
        'themes': themes
    }