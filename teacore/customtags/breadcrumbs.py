from django import template
from django.urls import reverse

register = template.Library()

@register.inclusion_tag('teacore/customtags/breadcrumbs.html')
def breadcrumbs(crumbs, divider="»"):
    breadcrumbs = []
    for index, crumb in enumerate(crumbs):
        if isinstance(crumb, tuple):
            name, url_name, *args = crumb
            url = reverse(url_name, args=args)
            breadcrumbs.append({ 'index': index, 'name': name, 'url': url })
        else:
            breadcrumbs.append({ 'index': index, 'name': crumb, 'url': None })  # Página actual, sin enlace

    return { 
        'breadcrumbs': breadcrumbs,
        'divider': divider 
    }