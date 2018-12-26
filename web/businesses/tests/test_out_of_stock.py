from django.test import TestCase
from django.utils import timezone
from mock import patch
from rest_framework import status
from rest_framework.reverse import reverse

from web.businesses.emails import EmailService
from web.businesses.es_service import BusinessLocationESService
from web.businesses.models import ReportOutOfStock, BusinessLocationMenuUpdate
from web.businesses.tests.factories import BusinessLocationMenuItemFactory
from web.search.vt_es_service import VtESService
from web.users.tests.factories import UserFactory


class OutOfStockTestCase(TestCase):

    @patch.object(EmailService, 'send_report_out_of_stock', return_value=None)
    @patch.object(BusinessLocationESService, 'save_menu_item', return_value=None)
    @patch.object(VtESService, 'save_vt', return_value=None)
    @patch.object(BusinessLocationMenuUpdate, 'record_business_location_menu_update', return_value=None)
    def setUp(self, *args):
        self.user = UserFactory()
        self.menu = BusinessLocationMenuItemFactory()
        self.url = reverse('businesses_api:business_location_report_out_of_stock',
                           args=(self.menu.business_location.business_id, self.menu.pk))

    def test_user_not_authorized(self):
        """
        Anonymous user does not have access to the analytics page
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(EmailService, 'send_report_out_of_stock', return_value=None)
    @patch.object(BusinessLocationESService, 'save_menu_item', return_value=None)
    @patch.object(VtESService, 'save_vt', return_value=None)
    @patch.object(BusinessLocationMenuUpdate, 'record_business_location_menu_update', return_value=None)
    @patch.object(BusinessLocationESService, 'save_business_location', return_value=None)
    def test_report_out_of_stock(self, *args):
        """
        User report out of stock
        """
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ReportOutOfStock.objects.count(), 1)
        report = ReportOutOfStock.objects.first()
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.menu_item, self.menu)

    @patch.object(EmailService, 'send_report_out_of_stock', return_value=None)
    @patch.object(BusinessLocationESService, 'save_menu_item', return_value=None)
    @patch.object(VtESService, 'save_vt', return_value=None)
    @patch.object(BusinessLocationMenuUpdate, 'record_business_location_menu_update', return_value=None)
    def test_report_out_of_stock_second_time(self, *args):
        """
        User report out of stock second time in 7 days after first report
        """
        report1 = ReportOutOfStock.objects.create(menu_item=self.menu, user=self.user,
                                                  created=timezone.now() - timezone.timedelta(days=5))
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ReportOutOfStock.objects.count(), 2)

        report = ReportOutOfStock.objects.first()
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.menu_item, self.menu)
        self.assertEqual(report.count, 2)
        self.assertTrue(report1.is_active)

        report1.refresh_from_db()
        self.assertFalse(report1.is_active)
        self.menu.refresh_from_db()
        self.assertFalse(self.menu.in_stock)

    @patch.object(EmailService, 'send_report_out_of_stock', return_value=None)
    @patch.object(BusinessLocationESService, 'save_menu_item', return_value=None)
    @patch.object(VtESService, 'save_vt', return_value=None)
    @patch.object(BusinessLocationMenuUpdate, 'record_business_location_menu_update', return_value=None)
    def test_report_out_of_stock_second_time_more_then_7_days(self, *args):
        """
        User report out of stock second time more the 7 days after first report
        """
        ReportOutOfStock.objects.create(menu_item=self.menu, user=self.user,
                                        start_timer=timezone.now()-timezone.timedelta(days=8))
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ReportOutOfStock.objects.count(), 2)

        report = ReportOutOfStock.objects.last()
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.menu_item, self.menu)

        self.menu.refresh_from_db()
        self.assertTrue(self.menu.in_stock)
