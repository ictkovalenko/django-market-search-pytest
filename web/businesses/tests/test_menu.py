import factory
from django.conf import settings
from django.utils import timezone
from mock import patch
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from web.businesses.emails import EmailService
from web.businesses.es_service import BusinessLocationESService
from web.businesses.models import ReportOutOfStock, BusinessLocationMenuUpdate, BusinessLocationMenuItem
from web.businesses.tests.factories import BusinessLocationMenuItemFactory, BusinessLocationFactory, BusinessFactory
from web.search.vt_es_service import VtESService
from web.search.tests.factories import VtFactory
from web.users.tests.factories import BusinessUserFactory


class MenuTestCase(APITestCase):

    @patch.object(EmailService, 'send_report_out_of_stock', return_value=None)
    @patch.object(VtESService, 'save_vt', return_value=None)
    @patch.object(BusinessLocationESService, 'save_menu_item', return_value=None)
    @patch.object(BusinessLocationESService, 'delete_menu_item', return_value=None)
    @patch.object(BusinessLocationMenuUpdate, 'record_business_location_menu_update', return_value=None)
    def setUp(self, *args):
        self.user = BusinessUserFactory()
        self.business = BusinessFactory(created_by=self.user)
        self.location = BusinessLocationFactory(business=self.business)
        self.vt = VtFactory()

        self.url = reverse('businesses_api:business_location_menu',
                           args=(self.location.business_id, self.location.pk))

        self.data = factory.build(dict, FACTORY_CLASS=BusinessLocationMenuItemFactory,
                                  vt_id=self.vt.pk, in_stock=True)
        self.data.pop('business_location')
        self.data.pop('vt')

    @patch.object(EmailService, 'send_report_out_of_stock', return_value=None)
    @patch.object(VtESService, 'save_vt', return_value=None)
    @patch.object(BusinessLocationESService, 'save_menu_item', return_value=None)
    @patch.object(BusinessLocationESService, 'delete_menu_item', return_value=None)
    @patch.object(BusinessLocationMenuUpdate, 'record_business_location_menu_update', return_value=None)
    def test_permissions(self, *args):
        """
        Only owner or staff of business can CRUD menu items
        """
        # Anonymous user
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Not owner
        self.client.force_login(self.user)
        location = BusinessLocationFactory()
        url = reverse('businesses_api:business_location_menu',
                      args=(location.business_id, location.pk))
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Allow any for readonly operations
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch.object(EmailService, 'send_report_out_of_stock', return_value=None)
    @patch.object(VtESService, 'save_vt', return_value=None)
    @patch.object(BusinessLocationESService, 'save_menu_item', return_value=None)
    @patch.object(BusinessLocationESService, 'delete_menu_item', return_value=None)
    @patch.object(BusinessLocationMenuUpdate, 'record_business_location_menu_update', return_value=None)
    def test_add(self, *args):
        """
        User successfully create menu
        """
        self.client.force_login(self.user)
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BusinessLocationMenuItem.objects.count(), 1)

        menu = BusinessLocationMenuItem.objects.first()
        self.assertEqual(menu.price_gram, self.data['price_gram'])
        self.assertEqual(menu.price_eighth, self.data['price_eighth'])
        self.assertEqual(menu.price_half, self.data['price_half'])
        self.assertEqual(menu.price_quarter, self.data['price_quarter'])
        self.assertEqual(menu.business_location_id, self.location.pk)
        self.assertEqual(menu.vt_id, self.vt.pk)
        self.assertTrue(menu.in_stock)

        self.assertEqual(response.json(), {
            'id': menu.id,
            'vt_id': menu.vt.id,
            'vt_name': menu.vt.name,
            'vt_variety': menu.vt.variety,
            'price_gram': menu.price_gram,
            'price_eighth': menu.price_eighth,
            'price_quarter': menu.price_quarter,
            'price_half': menu.price_half,
            'in_stock': menu.in_stock,
            'url': menu.vt.get_absolute_url(),
        })

    @patch.object(EmailService, 'send_report_out_of_stock', return_value=None)
    @patch.object(VtESService, 'save_vt', return_value=None)
    @patch.object(BusinessLocationESService, 'save_menu_item', return_value=None)
    @patch.object(BusinessLocationESService, 'delete_menu_item', return_value=None)
    @patch.object(BusinessLocationMenuUpdate, 'record_business_location_menu_update', return_value=None)
    def test_add_same_menu_item(self, *args):
        """
        User try to add already existed menu item but edit already existed
        """
        menu = BusinessLocationMenuItemFactory(vt=self.vt, business_location=self.location)

        self.client.force_login(self.user)
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(BusinessLocationMenuItem.objects.count(), 1)

        menu.refresh_from_db()
        self.assertEqual(menu.price_gram, self.data['price_gram'])
        self.assertEqual(menu.price_eighth, self.data['price_eighth'])
        self.assertEqual(menu.price_half, self.data['price_half'])
        self.assertEqual(menu.price_quarter, self.data['price_quarter'])
        self.assertEqual(menu.business_location_id, self.location.pk)
        self.assertEqual(menu.vt_id, self.vt.pk)
        self.assertTrue(menu.in_stock)

        self.assertEqual(response.json(), {
            'id': menu.id,
            'vt_id': menu.vt.id,
            'vt_name': menu.vt.name,
            'vt_variety': menu.vt.variety,
            'price_gram': menu.price_gram,
            'price_eighth': menu.price_eighth,
            'price_quarter': menu.price_quarter,
            'price_half': menu.price_half,
            'in_stock': menu.in_stock,
            'url': menu.vt.get_absolute_url(),
        })

    @patch.object(EmailService, 'send_report_out_of_stock', return_value=None)
    @patch.object(VtESService, 'save_vt', return_value=None)
    @patch.object(BusinessLocationESService, 'save_menu_item', return_value=None)
    @patch.object(BusinessLocationESService, 'delete_menu_item', return_value=None)
    @patch.object(BusinessLocationMenuUpdate, 'record_business_location_menu_update', return_value=None)
    def test_add_with_wrong_data(self, *args):
        """
        User submit wrong data and get error message
        """
        data = {
            'price_gram': 'test',
            'price_eighth': 'test',
            'price_quarter': 'test'
        }

        self.client.force_login(self.user)
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(BusinessLocationMenuItem.objects.count(), 0)
        self.assertEqual(response.json(), {
            'price_eighth': ['A valid number is required.'],
            'price_gram': ['A valid number is required.'],
            'price_quarter': ['A valid number is required.']})

    @patch.object(EmailService, 'send_report_out_of_stock', return_value=None)
    @patch.object(VtESService, 'save_vt', return_value=None)
    @patch.object(BusinessLocationESService, 'save_menu_item', return_value=None)
    @patch.object(BusinessLocationESService, 'delete_menu_item', return_value=None)
    @patch.object(BusinessLocationMenuUpdate, 'record_business_location_menu_update', return_value=None)
    def test_update_out_of_stock(self, *args):
        """
        User update out of stock attr
        """
        menu = BusinessLocationMenuItemFactory(vt=self.vt, business_location=self.location)
        data = {
            'menu_item': {
                'id': menu.pk,
                'in_stock': False
            }
        }

        self.client.force_login(self.user)
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(BusinessLocationMenuItem.objects.count(), 1)

    @patch.object(EmailService, 'send_report_out_of_stock', return_value=None)
    @patch.object(VtESService, 'save_vt', return_value=None)
    @patch.object(BusinessLocationESService, 'save_menu_item', return_value=None)
    @patch.object(BusinessLocationESService, 'delete_menu_item', return_value=None)
    @patch.object(BusinessLocationMenuUpdate, 'record_business_location_menu_update', return_value=None)
    def test_update_wrong_item(self, *args):
        """
        User try to update not his own menu item and get error
        """
        self.client.force_login(self.user)
        data = {
            'menu_item': {
                'id': BusinessLocationMenuItemFactory().pk,
                'in_stock': False
            }
        }
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch.object(EmailService, 'send_report_out_of_stock', return_value=None)
    @patch.object(VtESService, 'save_vt', return_value=None)
    @patch.object(BusinessLocationESService, 'save_menu_item', return_value=None)
    @patch.object(BusinessLocationESService, 'delete_menu_item', return_value=None)
    @patch.object(BusinessLocationMenuUpdate, 'record_business_location_menu_update', return_value=None)
    def test_update_out_of_stock_after_second_out_of_stock_report(self, *args):
        """
        User can't change out of stock attr next 10 days
        after second report that item is out of stock
        """
        menu = BusinessLocationMenuItemFactory(vt=self.vt, business_location=self.location, in_stock=False)
        ReportOutOfStock.objects.create(menu_item=menu, user=self.user, count=2,
                                        start_timer=timezone.now() - timezone.timedelta(days=8))
        data = {
            'menu_item': {
                'id': menu.pk,
                'in_stock': True
            }
        }

        self.client.force_login(self.user)
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(BusinessLocationMenuItem.objects.count(), 1)
        menu.refresh_from_db()
        self.assertFalse(menu.in_stock)

    @patch.object(EmailService, 'send_report_out_of_stock', return_value=None)
    @patch.object(VtESService, 'save_vt', return_value=None)
    @patch.object(BusinessLocationESService, 'save_menu_item', return_value=None)
    @patch.object(BusinessLocationESService, 'delete_menu_item', return_value=None)
    @patch.object(BusinessLocationMenuUpdate, 'record_business_location_menu_update', return_value=None)
    def test_update_out_of_stock_after_second_out_of_stock_report_was_expired(self, *args):
        """
        User can change out of stock attr after 10 days
        after second report that item is out of stock
        """
        menu = BusinessLocationMenuItemFactory(vt=self.vt, business_location=self.location, in_stock=False)
        ReportOutOfStock.objects.create(menu_item=menu, user=self.user, count=2,
                                        start_timer=timezone.now() - timezone.timedelta(days=11))
        data = {
            'menu_item': {
                'id': menu.pk,
                'in_stock': True
            }
        }

        self.client.force_login(self.user)
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(BusinessLocationMenuItem.objects.count(), 1)
        menu.refresh_from_db()
        self.assertTrue(menu.in_stock)

    @patch.object(EmailService, 'send_report_out_of_stock', return_value=None)
    @patch.object(VtESService, 'save_vt', return_value=None)
    @patch.object(BusinessLocationESService, 'save_menu_item', return_value=None)
    @patch.object(BusinessLocationESService, 'delete_menu_item', return_value=None)
    @patch.object(BusinessLocationMenuUpdate, 'record_business_location_menu_update', return_value=None)
    def test_list(self, *args):
        """
        User get menu list
        """
        menu1 = BusinessLocationMenuItemFactory(vt=self.vt, business_location=self.location, in_stock=False)
        menu2 = BusinessLocationMenuItemFactory(vt=self.vt, business_location=self.location)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [
            {
                'id': menu1.id,
                'vt_id': menu1.vt.id,
                'vt_name': menu1.vt.name,
                'vt_variety': menu1.vt.variety,
                'price_gram': menu1.price_gram,
                'price_eighth': menu1.price_eighth,
                'price_quarter': menu1.price_quarter,
                'price_half': menu1.price_half,
                'in_stock': menu1.in_stock,
                'url': menu1.vt.get_absolute_url(),
                'report_count': 0
            }, {
                'id': menu2.id,
                'vt_id': menu2.vt.id,
                'vt_name': menu2.vt.name,
                'vt_variety': menu2.vt.variety,
                'price_gram': menu2.price_gram,
                'price_eighth': menu2.price_eighth,
                'price_quarter': menu2.price_quarter,
                'price_half': menu2.price_half,
                'in_stock': menu2.in_stock,
                'url': menu2.vt.get_absolute_url(),
                'report_count': 0
            }
        ])

    @patch.object(EmailService, 'send_report_out_of_stock', return_value=None)
    @patch.object(VtESService, 'save_vt', return_value=None)
    @patch.object(BusinessLocationESService, 'save_menu_item', return_value=None)
    @patch.object(BusinessLocationESService, 'delete_menu_item', return_value=None)
    @patch.object(BusinessLocationMenuUpdate, 'record_business_location_menu_update', return_value=None)
    def test_delete(self, *args):
        """
        User successfully delete item
        """
        self.client.force_login(self.user)
        menu = BusinessLocationMenuItemFactory(vt=self.vt, business_location=self.location)
        data = {
            'menu_item_id': menu.pk
        }
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BusinessLocationMenuItem.objects.count(), 1)
        menu.refresh_from_db()
        self.assertEqual(menu.removed_date.date(), timezone.now().date())

    @patch.object(EmailService, 'send_report_out_of_stock', return_value=None)
    @patch.object(VtESService, 'save_vt', return_value=None)
    @patch.object(BusinessLocationESService, 'save_menu_item', return_value=None)
    @patch.object(BusinessLocationESService, 'delete_menu_item', return_value=None)
    @patch.object(BusinessLocationMenuUpdate, 'record_business_location_menu_update', return_value=None)
    def test_delete_wrong_item(self, *args):
        """
        User try to delete not existing item and receive error
        """
        self.client.force_login(self.user)
        data = {
            'menu_item_id': BusinessLocationMenuItemFactory().pk
        }
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(BusinessLocationMenuItem.objects.count(), 1)

    @patch.object(EmailService, 'send_report_out_of_stock', return_value=None)
    @patch.object(VtESService, 'save_vt', return_value=None)
    @patch.object(BusinessLocationESService, 'save_menu_item', return_value=None)
    @patch.object(BusinessLocationESService, 'delete_menu_item', return_value=None)
    @patch.object(BusinessLocationMenuUpdate, 'record_business_location_menu_update', return_value=None)
    def test_delete_then_add_same_menu_item(self, *args):
        """
        User successfully delete and then add same menu item
        """
        self.client.force_login(self.user)
        menu = BusinessLocationMenuItemFactory(vt=self.vt, business_location=self.location)
        data = {
            'menu_item_id': menu.pk
        }
        # Delete menu
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BusinessLocationMenuItem.objects.count(), 1)

        # Add menu
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(BusinessLocationMenuItem.objects.count(), 1)
        menu.refresh_from_db()
        self.assertIsNone(menu.removed_date)

    @patch.object(EmailService, 'send_report_out_of_stock', return_value=None)
    @patch.object(VtESService, 'save_vt', return_value=None)
    @patch.object(BusinessLocationESService, 'save_menu_item', return_value=None)
    @patch.object(BusinessLocationESService, 'delete_menu_item', return_value=None)
    @patch.object(BusinessLocationMenuUpdate, 'record_business_location_menu_update', return_value=None)
    def test_delete_then_add_same_menu_item_after_second_out_of_stock_report(self, *args):
        """
        User successfully delete and then add same menu item as "out of stock"
        next 10 days after second "out of stock" report
        """
        self.client.force_login(self.user)
        menu = BusinessLocationMenuItemFactory(vt=self.vt, business_location=self.location)
        ReportOutOfStock.objects.create(menu_item=menu, user=self.user, count=2,
                                        start_timer=timezone.now() - timezone.timedelta(days=8))
        data = {
            'menu_item_id': menu.pk
        }
        # Delete menu
        response = self.client.delete(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BusinessLocationMenuItem.objects.count(), 1)

        # Add menu
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(BusinessLocationMenuItem.objects.count(), 1)
        menu.refresh_from_db()
        self.assertIsNone(menu.removed_date)
        self.assertFalse(menu.in_stock)
