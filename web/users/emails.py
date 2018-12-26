import sendgrid
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from sendgrid.helpers.mail import *


class EmailService:
    host = settings.HOST

    basic_email_subject = 'VT: {0}'
    basic_email_with_link_pattern = '<html><body><div style="font-size: 18px">{text} ' \
                                    '<a href="{link_url}">link</a>.</div></body></html>'

    header_logo_url = staticfiles_storage.url('images/logo_hr.png')
    envelope_image_url = staticfiles_storage.url('images/email-envelope.png')
    leaf_image_url = staticfiles_storage.url('images/favicon.png')

    def send_confirmation_email(self, user):
        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)

        confirmation_url = '{host}{url}'.format(host=settings.HOST,
                                                url=reverse('users:confirm_email', kwargs={'uid': user.id}))
        logo_url = staticfiles_storage.url('images/logo_hr.png')
        fb_logo_url = staticfiles_storage.url('images/fb_logo_email_footer.png')

        html_template = render_to_string('emails/user_consumer_confirmation_email.html', {
            'user': user,
            'confirmation_url': confirmation_url,
            'logo_url': logo_url,
            'fb_logo_url': fb_logo_url,
            'fb_url': settings.FB_PROFILE_URL,
        })

        from_email = Email(settings.DEFAULT_FROM_EMAIL)
        to_email = Email(user.email)
        subject = self.basic_email_subject.format('Please verify your email address')

        html_content = Content('text/html', html_template)

        m = Mail(from_email, subject, to_email, html_content)
        return sg.client.mail.send.post(request_body=m.get())

    def send_reset_pwd_email(self, user, token):
        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)

        reset_url = '{host}{url}?uid={uid}&t={token}'.format(host=settings.HOST, url=reverse('account_reset_password'),
                                                             uid=str(user.id), token=token)

        html_content = self.basic_email_with_link_pattern.format(text='To reset your password click this',
                                                                 link_url=reset_url)

        from_email = Email(settings.DEFAULT_FROM_EMAIL)
        to_email = Email(user.email)
        subject = self.basic_email_subject.format('Reset Your Password')
        content = Content('text/html', html_content)

        m = Mail(from_email, subject, to_email, content)
        return sg.client.mail.send.post(request_body=m.get())
