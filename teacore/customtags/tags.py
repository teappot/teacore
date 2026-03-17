import uuid
from django.shortcuts import resolve_url
from django.utils.timezone import localtime
import pytz
from django import apps, template
from django.template.defaultfilters import stringfilter
from dateutil import parser
from teacore.assets.countryinfo import COUNTRYINFO  # Import the countries list
from django.utils.html import mark_safe
from django.conf import settings


register = template.Library()

@register.filter()
@stringfilter
def isoparse(value):
    return parser.isoparse(value)

@register.inclusion_tag('teacore/customtags/timezoneblock.html')
def timezoneblock(datetime, codes:str, styling=""):
    codes = [country.strip() for country in codes.upper().split(",")]
    
    countries = []
    for country in COUNTRYINFO:
        if country['code'] in codes:
            timezone = country['timezones'][0] if country['timezones'] else None
            tz = pytz.timezone(timezone)
    
            countries.append({
                'name': country['name'],
                'code': country['code'].lower(),
                'hour': localtime(datetime, tz).strftime("%H:%M"),
                'timezone': timezone
            }) 
    
    # Sort countries by hour
    countries.sort(key=lambda c: c['hour'])
    
    return { 
        'datetime': datetime,
        'countries': countries,
        'styling': styling
    }

@register.simple_tag
def link(url: str, *args, uuid: uuid.uuid4=None, slug: str=None, text: str=None, id: str=None, classes: str=None, target: str="_BLANK"):
    if uuid or slug:
        try:
            appmodel = url.split(":")
            model = apps.apps.get_model(appmodel[0], appmodel[1])
            obj = model.objects.get(uuid=uuid) if uuid else model.objects.get(slug=slug)
            url = obj.url() if obj.is_published else None 
        except Exception:
            url = resolve_url(url, *args)
    else:
        url = resolve_url(url, *args)

    text = url if text is None else text
    attrs = f'target="{target}"'
    attrs = f'class="{classes}" {attrs}' if classes else attrs
    attrs = f'id="{id}" {attrs}' if id else attrs

    if url:
        return mark_safe(f'<a href="{url}" {attrs}>{text}</a>')
    
    return mark_safe(f'<a {attrs}>{text}</a>')

@register.filter(name='equals')
def equals(value: any, compared: any):
    return (value == compared)

@register.simple_tag
def image(entity: str, id: int, alt: str="", classes: str="", style: str=""):
    """Render an <img> for a given entity model and id.
    `entity` can be in the form `app:Model` or `app.Model` or just `Model` (assumes `teacore`).
    The model must have an `image` field.
    """
    url = None
    try:
        if ":" in entity:
            app_label, model_name = entity.split(":", 1)
        elif "." in entity:
            app_label, model_name = entity.split(".", 1)
        else:
            app_label, model_name = ("teacore", entity)

        model = apps.apps.get_model(app_label, model_name)
        obj = model.objects.filter(id=id).first()
        if obj and getattr(obj, "image", None):
            img_field = getattr(obj, "image")
            url = img_field.url if hasattr(img_field, "url") else None
    except Exception:
        url = None

    url = url if url else f"{settings.STATIC_URL}img/no-image.jpg"

    return mark_safe(f'<img src="{url}" alt="{alt}" class="{classes}" style="{style}" />')