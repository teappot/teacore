from django import apps, template
from django.template.defaultfilters import stringfilter
from dateutil import parser
from django.utils.html import mark_safe
from django.db import models
from django.conf.urls.static import static
from django.conf import settings

register = template.Library()

@stringfilter
def isoparse(value):
    return parser.isoparse(value)

@register.filter(name="thumbnail")
def thumbnail(image: models.ImageField, default=""):
    if image: return image.url
    return f"{settings.STATIC_URL}/img/default.jpg"

@register.filter
def plainlist(rows, value: str="__str__"):
    return [getattr(row, value) for row in rows]