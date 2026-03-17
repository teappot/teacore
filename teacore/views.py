import base64
import json
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin import site
from django.utils.translation import get_language, gettext as _
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import HttpRequest
from django.shortcuts import redirect, render
from teacore.models import Widget
from django.conf import settings
from teacore.extras import async_send_mail
from django.apps import apps

# Create your views here.

@staff_member_required
def media_manager(request):
    import os
    import shutil
    from django.conf import settings

    root_path = settings.STATICFILES_DIRS[0]
    relative_path = request.GET.get('path', '')
    
    # Sanitize path to prevent directory traversal
    if '..' in relative_path or relative_path.startswith('/'):
        relative_path = ''
        
    current_path = os.path.join(root_path, relative_path)
    
    # Ensure we are still inside valid directories
    if not os.path.abspath(current_path).startswith(os.path.abspath(root_path)):
        current_path = root_path
        relative_path = ''

    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'create_folder':
            folder_name = request.POST.get('folder_name')
            if folder_name:
                new_folder_path = os.path.join(current_path, folder_name)
                try:
                    os.makedirs(new_folder_path, exist_ok=True)
                    messages.success(request, _('Folder created successfully.'))
                except Exception as e:
                    messages.error(request, f"Error creating folder: {e}")

        elif action == 'upload':
            if request.FILES.get('file'):
                uploaded_file = request.FILES['file']
                file_path = os.path.join(current_path, uploaded_file.name)
                try:
                    with open(file_path, 'wb+') as destination:
                        for chunk in uploaded_file.chunks():
                            destination.write(chunk)
                    messages.success(request, _('File uploaded successfully.'))
                except Exception as e:
                    messages.error(request, f"Error uploading file: {e}")

        elif action == 'delete':
            item_name = request.POST.get('item_name')
            item_path = os.path.join(current_path, item_name)
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                messages.success(request, _('Item deleted successfully.'))
            except Exception as e:
                messages.error(request, f"Error deleting item: {e}")
        
        return redirect(f"{request.path}?path={relative_path}")

    dirs = []
    files = []
    
    try:
        with os.scandir(current_path) as it:
            for entry in it:
                if entry.name.startswith('.'):
                    continue
                if entry.is_dir():
                    dirs.append(entry.name)
                else:
                    files.append(entry.name)
    except FileNotFoundError:
        messages.error(request, _('Path not found.'))
        return redirect(request.path)

    dirs.sort()
    files.sort()
    
    # Calculate parent path
    parent_path = None
    if relative_path:
        parent_path = os.path.dirname(relative_path)

    context = {
        'current_path': relative_path,
        'parent_path': parent_path,
        'dirs': dirs,
        'files': files,
        'app_label': 'teacore',
        'model_name': 'mediamanager',
        'title': 'Media Manager'
    }
    context.update(site.each_context(request))
    return render(request, 'admin/media-manager.html', context)

def widget(request, slug):

    widget = Widget.objects.filter(slug=slug, lang__code=get_language(), is_published=True).first()
    if widget is None:
        widget = Widget.objects.filter(slug=slug, lang__code=settings.LANGUAGE_CODE, is_published=True).first()

    response = render(request, "cms/widget.html", { "widget": widget })
    response["X-Robots-Tag"] = "noindex"

    return response

@staff_member_required
def template(request, template):
    template = template.replace(".", "/")
    context = request.GET.get("context", None)
    email = request.GET.get("email", None)

    if context:
        # Para enviar el context: context = base64.urlsafe_b64encode(json.dumps(context).encode()).decode()
        context = json.loads(base64.urlsafe_b64decode(context.encode()).decode())
        
    if email is not None:
        message = render_to_string(f"{template}.html", context=context, request=HttpRequest())
        async_send_mail(
            subject = "DEBUG: Teappot", 
            message = message, 
            recipient_list = [email]
        )

    return render(request, f"{template}.html", context)

@staff_member_required
def admin(request, app_label: str=None, model_name: str=None, id: int=None, method_name: str=None):
    try:
        model = apps.get_model(app_label=app_label, model_name=model_name)
        obj = model.objects.get(id=id)
        method = getattr(obj, method_name)
        if callable(method):
            method()
            messages.success(request, f"'{method_name}' executed successfully.")
        else:
            messages.error(request, f"'{method_name}' is not a callable method on {model_name}.")
    except model.DoesNotExist:
        messages.error(request, f"{model_name} with ID {id} not found.")
    except AttributeError:
        messages.error(request, f"Method '{method_name}' not found on {model_name} instance.")
    except Exception as e:
        messages.error(request, f"Exception: {e}")
    
    return redirect(request.environ['HTTP_REFERER'])

    