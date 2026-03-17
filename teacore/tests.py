from django.test import TestCase
from teacore.models import Mail, MailBlackListRule, MailSent
from django.conf import settings
import os

class MailSendTest(TestCase):
    def setUp(self):
        self.emails = [
            'walter.riedemann.j@gmail.com',         # No blacklisted
            'walter.riedemann.j+test@gmail.com',    # Blacklisted by name
            'walter.riedemann@ejemplo.com',         # Blacklisted by domain
            'walter.riedemann@conway.cl',           # No blacklisted
        ]
        # Blacklist por dominio y nombre
        MailBlackListRule.objects.create(text='@ejemplo.com', is_enabled=True)
        MailBlackListRule.objects.create(text='+test', is_enabled=True)

    def test_mail_send_with_blacklist(self):
        subject = 'Test Subject'
        template = 'mail.html'
        context = {'message': 'Test message'}
        recipients = self.emails.copy()

        # Enviar
        for recipient in recipients:
            Mail.send(subject, template, recipient, context)
        
        sent = MailSent.objects.all()
        sent_emails = [ms.mail.recipient for ms in sent]
        self.assertIn('walter.riedemann.j@gmail.com', sent_emails)
        self.assertIn('walter.riedemann@conway.cl', sent_emails)
        self.assertNotIn('walter.riedemann.j+test@gmail.com', sent_emails)
        self.assertNotIn('walter.riedemann@ejemplo.com', sent_emails)
        self.assertEqual(len(sent_emails), 2)