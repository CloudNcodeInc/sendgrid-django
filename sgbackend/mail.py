# -*- encoding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import sendgrid
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend
from email.mime.base import MIMEBase
try:
    import rfc822
except Exception as e:
    import email.utils as rfc822

from . import exceptions

__all__ = ('HANDLED_CONTENT_TYPES', 'SendGridBackend')

HANDLED_CONTENT_TYPES = {'text/html', 'text/plain'}


class SendGridBackend(BaseEmailBackend):
    """
    Email back-end using SendGrid Web API
    """

    def __init__(self, fail_silently=False, **kwargs):
        super(SendGridBackend, self).__init__(fail_silently=fail_silently, **kwargs)
        self.api_user = getattr(settings, 'SENDGRID_USER', None)
        self.api_key = getattr(settings, 'SENDGRID_PASSWORD', None)
        self.raise_unhandled = getattr(settings, 'SENDGRID_RAISE_UNHANDLED', False)
        if self.api_user is None or self.api_key is None:
            raise ImproperlyConfigured('Either SENDGRID_USER or SENDGRID_PASSWORD was not declared in settings.py')
        self.sendgrid = sendgrid.SendGridClient(self.api_user, self.api_key, raise_errors=not fail_silently)

    def open(self):
        pass

    def close(self):
        pass

    def send_messages(self, emails):
        """Sends one or more EmailMessage objects and returns the number of email messages sent."""

        if not emails:
            return
        count = 0
        for email in emails:
            try:
                self.sendgrid.send(self._build_sengrid_mail(email))
                count += 1
            except sendgrid.SendGridError:
                if not self.fail_silently:
                    raise
        return count

    def _build_sengrid_mail(self, email):
        mail = sendgrid.Mail()
        mail.add_to(email.to)
        mail.set_subject(email.subject)
        mail.set_from(email.from_email)

        text, html = '', email.body if email.content_subtype == 'html' else email.body, ''
        if hasattr(email, 'alternatives'):
            if self.raise_unhandled:
                unhandled_types = [t for c, t in email.alternatives if t not in HANDLED_CONTENT_TYPES]
                if unhandled_types:
                    raise exceptions.SendGridUnhandledContentTypeError(
                        "SendGrid API don't handle content of type(s) {0}".format(unhandled_types)
                    )
            if not html:
                try:
                    html = next(c for c, t in email.alternatives if t == 'text/html')
                except StopIteration:
                    pass
        mail.set_text(text)
        mail.set_html(html)

        for attachment in email.attachments:
            if isinstance(attachment, MIMEBase):
                mail.add_attachment_stream(attachment.get_filename(), attachment.get_payload())
            elif isinstance(attachment, tuple):
                mail.add_attachment_stream(attachment[0], attachment[1])

        if email.extra_headers:
            if 'Reply-To' in email.extra_headers:
                reply_to = rfc822.parseaddr(email.extra_headers['Reply-To'])[1]
                mail.set_replyto(reply_to)

            if 'Subs' in email.extra_headers:
                mail.set_substitutions(email.extra_headers['Subs'])

            if 'Sections' in email.extra_headers:
                mail.set_sections(email.extra_headers['Sections'])

            if 'Categories' in email.extra_headers:
                mail.set_categories(email.extra_headers['Categories'])

            if 'Unique-Args' in email.extra_headers:
                mail.set_unique_args(email.extra_headers['Unique-Args'])

            if 'Filters' in email.extra_headers:
                mail.data['filters'] = email.extra_headers['Filters']

            for attachment in email.attachments:
                mail.add_attachment_stream(attachment[0], attachment[1])

        return mail
