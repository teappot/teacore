import os
from django.apps import AppConfig
from django.conf import settings
from dotenv import load_dotenv
from pathlib import Path

class TeacoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "teacore"
    path = os.path.dirname(os.path.abspath(__file__))

    TRACK = (
        "TRACK_ANALITYCS",
        "TRACK_GOOGLETAG",
        "TRACK_PIXELMETA",
        "TRACK_TOKENMETA",
        "TRACK_CLARITY",
    )

    SOCIAL = (
        "SOCIAL_DISCORD",
        "SOCIAL_FACEBOOK",
        "SOCIAL_GITHUB",
        "SOCIAL_INSTAGRAM",
        "SOCIAL_LINKEDIN",
        "SOCIAL_LINKEDIN_COMPANY",
        "SOCIAL_MASTODON",
        "SOCIAL_REDDIT",
        "SOCIAL_TELEGRAM",
        "SOCIAL_THREADS",
        "SOCIAL_TIKTOK",
        "SOCIAL_TWITTER_X",
        "SOCIAL_WHATSAPP",
        "SOCIAL_YOUTUBE",
    )
    
    SHARE = (
        "SHARE_COPYLINK",
        "SHARE_FACEBOOK",
        "SHARE_INSTAGRAM",
        "SHARE_LINKEDIN",
        "SHARE_TELEGRAM",
        "SHARE_THREADS",
        "SHARE_TIKTOK",
        "SHARE_TWITTER_X",
        "SHARE_WHATSAPP",
    )

    def ready(self):
        load_dotenv()
        
        settings.LANGUAGE_CODE = str(os.getenv('LANGUAGE_CODE')) or "es"
        settings.TIME_ZONE = os.getenv('TIME_ZONE', "UTC")

        settings.APP_HOST = os.getenv('APP_HOST', "http://127.0.0.1:8000")
        settings.APP_NAME = str(os.getenv('APP_NAME'))
        settings.APP_LOGO = None
        settings.APP_TITLE = str(os.getenv('APP_TITLE'))
        settings.APP_SLOGAN = str(os.getenv('APP_SLOGAN', ''))
        settings.APP_AUTHOR = str(os.getenv('APP_AUTHOR', ''))

        for static_path in settings.STATICFILES_DIRS:
            if os.path.exists(os.path.join(static_path, 'img/logo.png')):
                settings.APP_LOGO = f"{settings.APP_HOST}/{settings.STATIC_URL}img/logo.png"
                break

        settings.META_DESCRIPTION = str(os.getenv('META_DESCRIPTION', ''))
        settings.META_KEYWORDS = str(os.getenv('META_KEYWORDS', ''))
        settings.META_AUTHOR = str(os.getenv('META_AUTHOR', ''))
        settings.META_COPYRIGHT = str(os.getenv('META_COPYRIGHT', ''))
        
        for name in self.TRACK + self.SOCIAL:
            setattr(settings, name, (os.getenv(name, None)))

        for name in self.SHARE:
            setattr(settings, name, (os.getenv(name, "False") == "True"))
        
        settings.THEME = str(os.getenv('THEME')) or 'none'
        settings.DARKMODE = str(os.getenv('DARKMODE')) or 'auto'

        BASE_DIR = Path(__file__).resolve().parent
        
        settings.TEMPLATES[0]["DIRS"].append(os.path.join(BASE_DIR, "templates"))
        settings.TEMPLATES[0]["OPTIONS"]["libraries"].update({
            "tea-tags": "teacore.customtags.tags",
            "tea-filters": "teacore.customtags.filters",
            "markdown": "teacore.customtags.markdown",
            "selectors": "teacore.customtags.selectors",
            "social": "teacore.customtags.social",
            "breadcrumbs": "teacore.customtags.breadcrumbs",
            "pagination": "teacore.customtags.pagination",
            "widget": "teacore.customtags.widget",
        })