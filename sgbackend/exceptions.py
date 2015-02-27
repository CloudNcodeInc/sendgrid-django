# -*- encoding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from sendgrid import exceptions


class SendGridUnhandledContentTypeError(exceptions.SendGridError):
    pass
