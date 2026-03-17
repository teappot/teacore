from django.shortcuts import redirect, resolve_url
from django.core.mail import send_mail

from django.conf import settings


def hx_redirect(to, *args, permanent=False, **kwargs):
    """
    Implementación de redirect con el header de HTMX para que funcione
    la redirección cuando está activado el hx-boost 
    """
    
    response = redirect(to, *args, permanent=permanent, **kwargs)
    response['HX-Redirect'] = resolve_url(to, *args, **kwargs)

    return response

def async_send_mail(subject, message, recipient_list, from_email=settings.EMAIL_DEFAULT_SENDER, auth_user=settings.EMAIL_HOST_USER):

    """
    import threading
    threading.Thread (
        target=send_mail,
        kwargs={
            'subject': subject,
            'message': message,
            'html_message': message,
            'from_email': from_email,
            'auth_user': auth_user,
            'recipient_list': recipient_list
    }).start()
    """
    res = send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        auth_user=auth_user,
        html_message=message,
    )
    print("res", res)

def csrf_failure(request, reason=""):
    """
    Implementación para evitar el error de CSRF al volver a la página
    """
    return redirect(resolve_url(request.META['PATH_INFO']))