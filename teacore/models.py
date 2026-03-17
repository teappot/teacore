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
        uuid_filename = f"{instance.IMAGEPATH}{str(instance.uuid)}{extension}"

        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, uuid_filename)):
            os.remove(os.path.join(settings.MEDIA_ROOT, uuid_filename))

        return filename

    @staticmethod
    def mediapath(instance, filename):
        return f"{instance.IMAGEPATH}{filename}"


# Abstracts
class TeaModelAbstract(models.Model):

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)

    # Metadata
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TeaPageAbstract(TeaModelAbstract):

    IMAGEPATH = ""
    VIEWNAME = ""

    lang = models.ForeignKey(Lang, on_delete=models.CASCADE, default=1)
    slug = models.SlugField(
        help_text=_("Para actualizar debe no debe estar publicado"),
        max_length=64,
        blank=True,
    )

    image = models.ImageField(
        upload_to=ImageHelper.mediapath, blank=True, null=True, default=None
    )
    title = models.CharField(
        max_length=64, blank=False, null=False
    )  # SEO: META_TITLE / schema: headline
    excerpt = models.CharField(
        max_length=155, blank=True, default=""
    )  # Para listados internos

    body = models.TextField(blank=True, default="")  # Markdown + Django tags
    draft = models.TextField(blank=True, default="")  # Markdown + Django tags
    version_draft = models.IntegerField(default=0)
    version_published = models.IntegerField(default=0)

    keywords = models.CharField(
        max_length=32, blank=True, default=""
    )  # SEO: META_KEYWORDS / schema: None
    description = models.CharField(
        max_length=155, blank=True, default=""
    )  # SEO: META_DESCRIPTION / schema: None
    noindex = models.BooleanField(default=False)
    nofollow = models.BooleanField(default=False)

    is_published = models.BooleanField(default=False)
    is_listed = models.BooleanField(
        help_text=_("Si se quiere mostrar en listas de categorías"), default=False
    )

    def context(self):
        setattr(self.image, "safe", (self.image.url if self.image else ""))
        return {
            "lang": {"code": self.lang.code, "name": self.lang.name},
            "title": self.title,
            "excerpt": self.excerpt,
            "image": self.image,
            "description": self.description,
            "keywords": self.keywords,
            "noindex": self.noindex,
            "nofollow": self.nofollow,
            "url": self.url(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def save(self, *args, **kwargs):
        try:
            previous = type(self).objects.get(pk=self.pk)
        except type(self).DoesNotExist:
            previous = None

        if self.slug is None or self.slug == "":
            self.slug = slugify(self.title).lower()
        elif not self.is_published:
            self.slug = slugify(self.title).lower()

        if previous:
            if self.draft != previous.draft:
                self.version_draft += 1

            if previous.image and self.image != previous.image:
                if hasattr(previous.image, "path") and os.path.isfile(
                    previous.image.path
                ):
                    os.remove(previous.image.path)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image and hasattr(self.image, "path"):
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)

        super().delete(*args, **kwargs)

    def publish(self):
        if self.draft == "":
            self.draft = self.body

        self.body = self.draft
        self.version_published = self.version_draft
        self.save()

    @classmethod
    def get_or_404(cls, slug: str = None, uuid: uuid.uuid4 = None):
        page = cls.get(slug, uuid)
        if page is None:
            raise Http404()

        return page

    @classmethod
    def get(cls, slug: str = None, uuid: uuid.uuid4 = None):
        if slug:
            lang = Lang.current()
            page = cls.objects.filter(slug=slug, lang=lang).first()
            if page is None:
                page = cls.objects.filter(slug=slug).first()
            return page
        elif uuid:
            return cls.objects.filter(uuid=uuid).first()

    def url(self):
        from django.urls import get_resolver, get_urlconf

        url_resolver = get_resolver(get_urlconf())
        registered_namespaces = url_resolver.namespace_dict.keys()

        print(registered_namespaces)
        return resolve_url(self.VIEWNAME, self.slug)

    @classmethod
    def list(cls, page=1, lang=settings.LANGUAGE_CODE, is_published=True):
        objects = cls.objects.filter(lang__code=lang, is_published=is_published)
        paginator = Paginator(objects, settings.CMS_PAGINATION)

        return paginator.get_page(page)

    def __str__(self):
        return f"{self.lang.code}, {self.slug} ({self.id})"

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["slug"], name="%(app_label)s_%(class)s_unique_uuid"
            )
        ]


def page_image_upload_to(instance, filename):
    parent = getattr(instance, 'parent', None)
    if parent:
        # Use the parent's model name as the top-level folder
        model_name = parent.__class__.__name__.lower()
        return f"{model_name}/{instance.uuid}/{filename}"

    return f"{instance.uuid}/{filename}"

class PageAbstractImage(TeaModelAbstract):

    image = models.ImageField(upload_to=page_image_upload_to, blank=True, null=True, default=None)
    alt = models.CharField(max_length=128, blank=True, help_text=_("Texto alternativo para la imagen"))
    tags = models.CharField(max_length=64, blank=True, help_text=_("Etiquetas separadas por comas para búsqueda"))

    def delete(self, *args, **kwargs):
        if self.image and hasattr(self.image, 'path'):
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.pk:
            old = type(self).objects.get(pk=self.pk)
            if old.image and old.image != self.image:
                if hasattr(old.image, 'path') and os.path.isfile(old.image.path):
                    os.remove(old.image.path)
        super().save(*args, **kwargs)

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
