import calendar
import time

import sendgrid
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from sendgrid.helpers.mail import Email, Content, Mail, Personalization

from web.common import html


class EmailService:
    host = settings.HOST

    basic_email_subject = ': {0}'
    basic_email_with_link_pattern = '<html><body><div style="font-size: 18px">{text} ' \
                                    '<a href="{link_url}">link</a>.</div></body></html>'

    header_logo_url = staticfiles_storage.url('images/logo_hr.png')
    envelope_image_url = staticfiles_storage.url('images/email-envelope.png')
    leaf_image_url = staticfiles_storage.url('images/favicon.png')

    @staticmethod
    def get_client():
        return sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)

    def send_confirmation_email(self, user):
        sg = self.get_client()

        confirmation_url = '{host}{url}'.format(host=settings.HOST,
                                                url=reverse('businesses:confirm_email', kwargs={'uid': user.id}))

        from_email = Email(settings.DEFAULT_FROM_EMAIL)
        to_email = Email(user.email)
        subject = self.basic_email_subject.format('Verify Your Email')

        html_template = render_to_string('emails/user_consumer_confirmation_email.html', {
            'confirmation_url': confirmation_url,
            'sent_to': user.email,
            'header_logo_url': self.header_logo_url,
            'envelope_image_url': self.envelope_image_url,
            'leaf_image_url': self.leaf_image_url
        })

        html_content = Content('text/html', html_template)

        m = Mail(from_email, subject, to_email, html_content)
        return sg.client.mail.send.post(request_body=m.get())

    def send_menu_update_request_email(self, update_request):
        sg = self.get_client()

        location = update_request.business_location
        user = update_request.user
        message = update_request.message

        from_email = Email(settings.DEFAULT_FROM_EMAIL)
        to_email = Email(location.location_email)
        cc_email = Email(settings.CC_DEFAULT_EMAIL)

        subject = 'Menu Update Request'

        html_template = render_to_string('emails/business_menu_update_request.html', {
            'business_location': location,
            'user': user,
            'header_logo_url': staticfiles_storage.url('images/logo_hr.png'),
            'envelope_image_url': staticfiles_storage.url('images/email-envelope.png'),
            'message': html.sanitize(message.replace('\n', '<br>')),
            'location_url': settings.HOST + location.urls.get('dispensary'),
            'login_url': settings.HOST + reverse('account_login'),
            'claim_url': settings.HOST + reverse('businesses:claim_options'),
            'update_date_url': settings.HOST + reverse('businesses:confirm_menu',
                                                       kwargs={'secret_key': update_request.secret_key}),
        })
        html_content = Content('text/html', html_template)

        m = Mail(from_email, subject, to_email, html_content)
        personalization = Personalization()
        personalization.add_cc(cc_email)
        personalization.add_to(to_email)
        m.add_personalization(personalization)

        return sg.client.mail.send.post(request_body=m.get())

    def send_menu_update_request_served_email(self, update_request):
        sg = self.get_client()

        location = update_request.business_location
        user = update_request.user

        from_email = Email(settings.DEFAULT_FROM_EMAIL)
        to_email = Email(user.email)

        subject = 'Menu Update Request'

        html_template = render_to_string('emails/business_menu_update_request_served.html', {
            'business_location': location,
            'user': user,
            'header_logo_url': staticfiles_storage.url('images/logo_hr.png'),
            'envelope_image_url': staticfiles_storage.url('images/email-envelope.png'),
            'location_url': settings.HOST + location.urls.get('dispensary'),
        })
        html_content = Content('text/html', html_template)

        m = Mail(from_email, subject, to_email, html_content)

        # 10 min from now
        m.send_at = int(calendar.timegm(time.gmtime())) + 600

        return sg.client.mail.send.post(request_body=m.get())

    def send_business_claim_request_served_email(self, context):
        sg = self.get_client()

        from_email = Email(settings.DEFAULT_FROM_EMAIL)
        to_email = Email('')

        subject = 'Business Claim Request'

        html_template = render_to_string('emails/business_claim_request.html', context)
        html_content = Content('text/html', html_template)

        m = Mail(from_email, subject, to_email, html_content)
        return sg.client.mail.send.post(request_body=m.get())

    def send_report_out_of_stock(self, menu, is_second=False):
        sg = self.get_client()

        from_email = Email(settings.DEFAULT_FROM_EMAIL)
        to_email = Email(menu.business_location.location_email)
        cc_email = Email(settings.CC_DEFAULT_EMAIL)

        subject = 'Out Of Stock'
        context = {
            'name': menu.business_location.business.name,
            'vt': menu.vt.name,
            'days_count': settings.PERIOD_BLOCK_MENU_ITEM_OUT_OF_STOCK,
            'header_logo_url': settings.HOST + self.header_logo_url,
            'envelope_image_url': settings.HOST + self.envelope_image_url,
            'leaf_image_url': settings.HOST + self.leaf_image_url,
            'login_url': '{}{}?next={}'.format(
                settings.HOST, reverse('account_login'),
                reverse('businesses:menu', args=(menu.business_location.business.pk, 'menu'))),
            'claim_url': settings.HOST + reverse('businesses:claim_options'),
        }
        if is_second:
            html_template = render_to_string('emails/second_report_out_of_stock.html', context)
        else:
            html_template = render_to_string('emails/report_out_of_stock.html', context)

        html_content = Content('text/html', html_template)
        m = Mail(from_email, subject, to_email, html_content)

        personalization = Personalization()
        personalization.add_cc(cc_email)
        personalization.add_to(to_email)
        m.add_personalization(personalization)

        return sg.client.mail.send.post(request_body=m.get())
