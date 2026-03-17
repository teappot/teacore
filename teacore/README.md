## Settings

Agregar a settings.py:

```python
MIDDLEWARE = [
    ...
    "django.middleware.locale.LocaleMiddleware",
    "teacore.middleware.LanguageCookieMiddleware.LanguageCookieMiddleware",
    "teacore.middleware.ThemeCookieMiddleware.ThemeCookieMiddleware",
    "teacore.middleware.HtmxAuthRedirectMiddleware.HtmxAuthRedirectMiddleware",
    ...
]
```

```python
TEMPLATES = [
    {
        ...
        "OPTIONS": {
            "context_processors": [
                ...
                "teacore.context.context",
            ],
            ...
        },
    },
]
```


# Templates

## Filters

**plainlist**: retorna una lista con los valores de un atributo de un resultset.

```html
{% load teatags %}

<span>
    {{ rows|plainlist:"attribute_name"|join:", " }}
</span>
```