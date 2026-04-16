from django.db import models
import os, uuid
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.conf import settings
from teacore.extras import async_send_mail
from django.utils.text import slugify
from django.shortcuts import resolve_url
from django.utils.translation import gettext as _
from django.utils import translation
from django.core.paginator import Paginator
from django.http import Http404

# Base Models
class Lang(models.Model):

    code = models.CharField(
        max_length=2, editable=False, unique=True
    )  # ISO 639 https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes
    name = models.CharField(
        max_length=64,
        editable=False,
        help_text="Use only endonym (the country name in his own languaje)",
    )

    is_default = models.BooleanField(default=False, editable=False)
    is_enabled = models.BooleanField(default=False)

    def save(self, *args, **kwargs):

        if self.is_default:
            Lang.objects.all().update(is_default=False)
            self.is_enabled = True

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return  # cannot be deleted

    @classmethod
    def set_default(cls, code):
        cls.objects.all().update(is_default=False)

        lang = cls.objects.get(code=code)
        lang.is_default = True
        lang.is_enabled = True
        lang.save()

        return lang

    @classmethod
    def get_default(cls):
        return cls.objects.get(is_default=True)
    
    @classmethod
    def current(cls):
        code = translation.get_language()
        lang = cls.objects.filter(code=code, is_enabled=True).first()
        return lang if lang else cls.get_default()

    def __str__(self):
        return "{} ({})".format(self.code, self.name)

    class Meta:
        verbose_name = "Language"
        verbose_name_plural = "Languages"


class ImageHelper:

    @staticmethod
    def rename_to_uuid(instance, filename):
        _, extension = os.path.splitext(instance.image.name)
        uuid_filename = f"{instance.IMAGEPATH}/{str(instance.uuid)}{extension}"

        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, uuid_filename)):
            os.remove(os.path.join(settings.MEDIA_ROOT, uuid_filename))

        return uuid_filename

    @staticmethod
    def mediapath(instance, filename):
        return f"{instance.IMAGEPATH}/{filename}"


# Abstracts
class TeaModelAbstract(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)

    # Metadata
    is_enabled = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def trash(self):
        """Soft delete"""
        self.is_deleted = True
        self.save()

    def delete(self, hard=True, *args, **kwargs):
        if hard:
            super().delete(*args, **kwargs)
            return
        
        self.trash()

    class Meta:
        abstract = True

class TeaGuestAbstract(TeaModelAbstract):

    # Metadata
    name = models.CharField(max_length=96, blank=True)
    phone = models.CharField(max_length=96, blank=True)
    email = models.EmailField(blank=False)

    metadata = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        abstract = True


# Modelos
class MailBlackListRule(TeaModelAbstract):

    text = models.CharField(max_length=192, unique=True)
    is_enabled = models.BooleanField(default=False)

    @classmethod
    def is_blacklisted(cls, recipient: str, request=None):

        blacklist = cls.objects.filter(is_enabled=True).values_list("text", flat=True)
        is_blacklist = any(text in recipient for text in blacklist)
        if is_blacklist:
            MailBlackListed.create(recipient, request)

        return is_blacklist


class MailBlackListed(TeaModelAbstract):

    recipient = models.EmailField()
    request = models.JSONField()

    @classmethod
    def create(cls, recipient: str, request=None):

        request = request.__dict__ if request else []
        cls.objects.create(recipient=recipient, request=request)


class Mail(models.Model):

    recipient = models.EmailField(unique=True)
    opt_in = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def send(
        cls,
        subject: str,
        recipient: str,
        template: str,
        context: dict,
        sender: str = settings.EMAIL_DEFAULT_SENDER,
        app: str = "",
        user: User = None,
        request=None,
    ):
        if not MailBlackListRule.is_blacklisted(recipient=recipient, request=request):
            mail = cls.objects.get_or_create(recipient=recipient)[0]
            MailSent.create(
                mail=mail,
                app=app,
                user=user,
                subject=subject,
                template=template,
                sender=sender,
            )

            message = render_to_string(template, context=context, request=HttpRequest())
            async_send_mail(
                subject=f"{subject} | {settings.APP_TITLE}",
                message=message,
                recipient_list=[recipient],
            )
            return True

        return False


class MailSent(models.Model):

    mail = models.ForeignKey(Mail, on_delete=models.CASCADE, related_name="sent")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="mailsent", null=True
    )
    app = models.CharField(max_length=64)

    subject = models.CharField(max_length=192)
    template = models.CharField(max_length=96)
    sender = models.EmailField()

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create(
        cls,
        mail: Mail,
        subject: str,
        template: str,
        sender: str,
        app: str = "",
        user: User = None,
    ):

        cls.objects.create(
            mail=mail,
            user=user,
            app=app,
            subject=subject,
            template=template,
            sender=sender,
        )


class Widget(TeaModelAbstract):

    lang = models.ForeignKey(Lang, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=64, blank=False, null=False)

    body = models.TextField()  # Markdown

    is_published = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["slug", "lang"], name="widget_unique_slug_lang"
            )
        ]

    def __str__(self):
        return self.slug


# Mocks
class MediaManager(models.Model):
    
    class Meta:
        verbose_name = "Media Manager"
        verbose_name_plural = "Media Manager"
