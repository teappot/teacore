from django import template
from django.conf import settings

register = template.Library()

@register.inclusion_tag('teacore/customtags/social-links.html')
def social_links(show_names=False):

    social = {
        key: getattr(settings, key) 
        for key in dir(settings) 
        if key.startswith("SOCIAL_")
    }
    social.update({
        'show_names': show_names
    })

    return social

@register.inclusion_tag('teacore/customtags/social-share.html')
def social_share():
    
    return {
        key: getattr(settings, key) 
        for key in dir(settings) 
        if key.startswith("SHARE_")
    }