from teacore.models import Widget
from django.conf import settings
from django.utils.translation import get_language
from django import template
from django.utils import timezone
from datetime import timedelta
from django.utils.safestring import mark_safe
from urllib.parse import quote

register = template.Library()

@register.inclusion_tag('teacore/customtags/widget.html')
def widget(slug):
    widget = Widget.objects.filter(slug=slug, lang__code=get_language(), is_published=True).first()
    if widget is None:
        widget = Widget.objects.filter(slug=slug, lang__code=settings.LANGUAGE_CODE, is_published=True).first()
            
    return { 
        'widget': widget
    }

@register.inclusion_tag('teacore/customtags/whatsapp.html')
def whatsapp(text, phone=None):
            
    return { 
        'phone': phone if phone else settings.SOCIAL_WHATSAPP,
        'text': text,
    }


@register.inclusion_tag('teacore/customtags/addcalendar.html')
def addcalendar(text, details, location, start, end):
    dates = f"{start}/{end}"

    return {
        'google': f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={text}&details={details}&dates={dates}&location={location}",
        'outlook': f"https://outlook.live.com/calendar/0/deeplink/compose?&subject={text}&body={details}&startdt={start}&enddt={end}&location={location}&path=%2Fcalendar%2Faction%2Fcompose&rru=addevent",
        'ics': f"data:text/calendar;charset=utf8,BEGIN:VCALENDAR%0AVERSION:2.0%0ABEGIN:VEVENT%0ADTSTART:{start}%0ADTEND:{end}%0ASUMMARY:{text}%0ADESCRIPTION:{details}%0AURL:{location}%0AALOCATION:{location}%0AEND:VEVENT%0AEND:VCALENDAR%0A"
    }