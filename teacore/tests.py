from django.test import TestCase
from teacore.models import Mail, MailBlackListRule, MailSent
from django.conf import settings
import os

class MailSendTest(TestCase):
    def setUp(self):
        self.emails = [
            'username@gmail.com',         # No blacklisted
            'username+test@gmail.com',    # Blacklisted by name
            'username@ejemplo.com',         # Blacklisted by domain
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
        self.assertIn('username@gmail.com', sent_emails)
        self.assertNotIn('username+test@gmail.com', sent_emails)
        self.assertNotIn('username@ejemplo.com', sent_emails)
        self.assertEqual(len(sent_emails), 1)