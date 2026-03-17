from django.contrib import admin
from django.utils.html import mark_safe
from django.utils.translation import gettext as _
from teacore.models import Lang, Mail, MailBlackListRule, MailBlackListed, MailSent, Widget, MediaManager
from django.conf import settings

from django.urls import path, reverse
from django.template.response import TemplateResponse

# Register your models here.
@admin.action(permissions=['change',])
def publish(self, request, queryset):
    for item in queryset:
        item.publish()
    self.message_user(request, "item(s) published successfully.")

def custom_list(obj:admin.ModelAdmin, attr:str, index:str, fields:list):
    if hasattr(obj, attr):
        lst = list(getattr(obj, attr))
        index = lst.index(index) if index in lst else 0
        lst[index:index] = fields
        return lst
    
class TeaPageAdmin(admin.ModelAdmin):

    save_on_top = True
    actions = [publish]

    list_display = ['uuid', 'slug', 'lang', 'title', 'updated_at', 'is_published',]
    list_filter = ['is_published',]
    
    search_fields = ['title', 'draft', 'body', 'excerpt', 'keywords', 'description',]

    fields = ['link', 'uuid', 'slug', 'lang', 'image', 'title', 'excerpt', 'keywords', 'description', 'draft', 'publish', 'is_published', 'is_listed',]
    readonly_fields = ['link', 'publish','uuid', 'slug',]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['draft'].widget.attrs['class'] = 'markdown'
        form.base_fields['lang'].queryset = Lang.objects.filter(is_enabled=True)
        
        return form
    
    def publish(self, obj):
        viewname = self.model.VIEWNAME.split(":")
        return mark_safe(f'<a class="btn-action" href="{settings.APP_HOST}/teacore/admin/{viewname[0]}/{viewname[1]}/{obj.id}/publish">\
            <b>{_("Publicar")}</b>: v{obj.version_published} » v{obj.version_draft}</a>')
    
    def link(self, obj):
        try:
            return mark_safe(f"""
                <a href="{settings.APP_HOST}{obj.url()}?draft=true" target="_blank">{obj.url()} [draft]</a>
                &nbsp;&nbsp;|&nbsp;&nbsp;
                <a href="{settings.APP_HOST}{obj.url()}" target="_blank">[published]</a>
            """)
        except Exception as e:
            print("TeaPageAdmin error", e)
            return ""

@admin.register(Lang)
class LangAdmin(admin.ModelAdmin):
    model = Lang
    actions = None

    list_display = ["name", "code", "is_default", "is_enabled", ]
    list_filter = ["is_enabled", ]
    list_editable = ["is_enabled", ]
    fields = ["name", "code", "is_enabled", "is_default", ]
    readonly_fields = ["name", "code", "is_default", ]

    save_on_top = True
    
    def has_delete_permission(self, request, obj=None):
      return False

    def has_add_permission(self, request):
      return False
    
@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    model = Widget
    save_on_top = True

    list_display = ['slug', 'lang', 'is_published',]
    list_filter = ['is_published',]
    list_editable = []
    search_fields = ['slug', 'body',]
    fields = ['tag', 'slug', 'lang', 'body', 'is_published',]
    readonly_fields = ['tag']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['lang'].queryset = Lang.objects.filter(is_enabled=True)
        form.base_fields['body'].widget.attrs['class'] = 'markdown'
        
        return form
    
    def tag(self, obj):
        if obj.slug:
            return str(f"{{% widget \"{obj.slug}\" %}}")
        return "-"
    

class MailSentInline(admin.TabularInline):
    model = MailSent
    extra = 0

    fields = ['username', 'app', 'subject', 'template', 'sender']
    readonly_fields = ['username', 'app', 'subject', 'template', 'sender']

    def username(self, obj):
        if obj.user:
            return obj.user.username
        return "-"
    

@admin.register(Mail)
class MailAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'opt_in']
    inlines = [MailSentInline]

@admin.register(MailBlackListed)
class MailBlackListedAdmin(admin.ModelAdmin):
    list_display = ['recipient']

@admin.register(MailBlackListRule)
class MailBlackListRuleAdmin(admin.ModelAdmin):
    list_display = ['text', 'is_enabled']


@admin.register(MediaManager)
class MediaManagerAdmin(admin.ModelAdmin):
    
    def changelist_view(self, request, extra_context=None):
        from teacore.views import media_manager
        
        return media_manager(request)