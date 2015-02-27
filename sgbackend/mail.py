# -*- encoding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import sendgrid
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend

from . import utils

__all__ = ('SendGridBackend', )


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
                self.sendgrid.send(utils.build_sengrid_mail(email, check=self.raise_unhandled))
                count += 1
            except sendgrid.SendGridError:
                if not self.fail_silently:
                    raise
        return count
