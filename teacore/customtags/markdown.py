from django import template
from django.http import HttpRequest
from django.template.defaultfilters import stringfilter
from django.template import engines

import markdown as md

register = template.Library()

@register.filter()
@stringfilter
def markdown(value, request=None):
    context = request.context if hasattr(request, 'context') else {}
    value = engines['django'].from_string("\n".join([
        "{% load static %}", 
        "{% load i18n %}", 
        "{% load widget %}", 
        "{% load tea-tags %}", 
        "{% load markdown %}", 
        value
    ])).render(request=request, context=context)
    
    return md.markdown(value, extensions=['markdown.extensions.fenced_code'])


@register.inclusion_tag('teacore/customtags/mdfile.html')
def mdfile(filename, styling=""):
    title = None
    body = []
    filepath = f"assets/markdown/{filename}.md"  # Construct the full path
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("# ") and title is None:
                title = line[2:].strip()  # Extract title without "# "
            else:
                body.append(line)
    
    return { 
        'title': title,
        'body': ''.join(body),
        'filename': filename,
        'styling': styling
    }

@register.inclusion_tag('teacore/customtags/mdread.html')
def mdread(filename, styling=""):
    title = None
    filepath = f"assets/markdown/{filename}.md"
    body = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("# ") and title is None:
                title = line[2:].strip()  # Extract title without "# "
            else:
                body.append(line)

    return {
        'body': ''.join(body),
        'filename': filename,
        'styling': styling
    }

@register.filter()
@stringfilter
def styling(role, theme):

    if role == "alert":
        return f"alert alert-{theme}"
    
    theme = "danger" if theme == "error" else theme
    text = "light" if theme in ["success","info","danger"] else "dark"

    if role in ["blockquote","toast"]:
        return f"bg-{theme} bs-{text}"
    
    if role in ["btn","btn-outline"]:
        text = "dark" if theme in ["success","danger"] else "light"
        return f"{role}-{theme} bs-{text}"