# -*- encoding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import sendgrid
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend

from . import utils

__all__ = ('SendGridBackend', )


class SendGridBackend(BaseEmailBackend):
    """Email back-end using SendGrid Web API"""

    def __init__(self, fail_silently=False, **kwargs):
        super(SendGridBackend, self).__init__(
            fail_silently=fail_silently, **kwargs)
        self.api_key = getattr(settings, 'SENDGRID_API_KEY', None)
        self.api_user = getattr(settings, 'SENDGRID_USER', None)
        self.api_password = getattr(settings, 'SENDGRID_PASSWORD', None)
        self.raise_unhandled = getattr(settings, 'SENDGRID_RAISE_UNHANDLED', False)

        credentials = []
        if self.api_key:
            credentials.append(self.api_key)
        elif self.api_user and self.api_password:
            credentials.append(self.api_user)
            credentials.append(self.api_password)
        else:
            raise ImproperlyConfigured('Either SENDGRID_API_KEY or both (SENDGRID_USER and SENDGRID_PASSWORD) '
                                       'must be declared in settings.py')
        self.sg = sendgrid.SendGridClient(*credentials, raise_errors=not fail_silently)

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
                self.sendgrid.send(utils.build_sengrid_mail(email, check=self.raise_unhandled))
                count += 1
            except sendgrid.SendGridError:
                if not self.fail_silently:
                    raise
        return count
