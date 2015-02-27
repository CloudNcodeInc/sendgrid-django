
import sendgrid
from email.mime.base import MIMEBase
try:
    import rfc822
except Exception as e:
    import email.utils as rfc822

from . import exceptions

__all__ = ('HANDLED_CONTENT_TYPES', 'build_sengrid_mail', 'is_handled')

HANDLED_CONTENT_TYPES = {'text/html', 'text/plain'}


def build_sengrid_mail(email, check=True, fail=True):
    if check and not is_handled(email, fail=fail):
        return

    mail = sendgrid.Mail()
    mail.add_to(email.to)
    mail.set_subject(email.subject)
    mail.set_from(email.from_email)

    text, html = '', email.body if email.content_subtype == 'html' else email.body, ''
    if not html and hasattr(email, 'alternatives'):
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


def is_handled(email, fail=True):
    if hasattr(email, 'alternatives'):
        unhandled_types = [t for c, t in email.alternatives if t not in HANDLED_CONTENT_TYPES]
        if unhandled_types:
            if fail:
                raise exceptions.SendGridUnhandledContentTypeError(
                    "SendGrid API don't handle content of type(s) {0}".format(unhandled_types)
                )
            return False
    return True
