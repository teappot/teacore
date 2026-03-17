from django import template

register = template.Library()

@register.inclusion_tag('teacore/customtags/pagination.html')
def pagination(objects):
            
    return { 
        'objects': objects
    }