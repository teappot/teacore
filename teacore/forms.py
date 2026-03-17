from django import forms
from django.utils.translation import gettext as _

class SimpleContactForm(forms.Form):

    name = forms.CharField(label = _("Nombre"),
        widget = forms.TextInput(attrs={ 'placeholder': _("Nombre"), 'max_length': 96, 'class': "form-control" }),
        required=True )
    
    phone = forms.CharField(label = _("Teléfono"),
        widget = forms.TextInput(attrs={ 'placeholder': _("Teléfono"), 'max_length': 16, 'class': "form-control" }),
        required=False )
    
    email = forms.CharField(label = _("Email"),
        widget = forms.TextInput(attrs={ 'placeholder': _("email"), 'max_length': 96, 'class': "form-control text-lowercase" }),
        required=True )

    def clean_name(self):
        email = self.cleaned_data.get('name').strip()
        return email
    
    def clean_phone(self):
        email = self.cleaned_data.get('phone').strip()
        return email
    
    def clean_email(self):
        email = self.cleaned_data.get('email').strip().lower()
        return email