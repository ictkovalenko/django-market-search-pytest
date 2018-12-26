from __future__ import unicode_literals, absolute_import

from django.db import models
from django.conf import settings
from django.utils import timezone


class BusinessLocationMenuUpdateRequestQuerySet(models.QuerySet):

    def events(self, from_date, to_date, entity_id):
        query = self.filter(business_location__business_id=entity_id)
        if from_date:
            query = query.filter(date_time__gte=from_date)

        if to_date:
            query = query.filter(date_time__lte=to_date)
        return query

    def group_by_day(self):
        return self \
            .extra(select={'day': 'to_char( date_time,  \'YYYY-MM-DD\' )'}) \
            .values('day') \
            .annotate(count=models.Count('date_time')) \
            .order_by('day')


class MenuItemQuerySet(models.QuerySet):

    def avg_8th_price(self, location):
        return self.filter(business_location=location) \
            .aggregate(avg_price=models.Avg('price_eighth'))['avg_price']

    def reports(self):
        return self.annotate(report_count=models.Sum(
            models.Case(
                models.When(reports__count__gte=2,
                            reports__is_active=True,
                            reports__start_timer__gte=timezone.now() - timezone.timedelta(
                                days=settings.PERIOD_BLOCK_MENU_ITEM_OUT_OF_STOCK),
                            then=1),
                default=0,
                output_field=models.IntegerField(),
            )
        ))


class ReportOutOfStockQuerySet(models.QuerySet):

    def is_out_of_stock_reports(self, menu):
        """
        Check if menu item was reported as out of stock two times
        :param menu: BusinessLocationMenuItem instance
        :return: boolean
        """
        return self.filter(
            menu_item=menu, count=2, is_active=True,
            start_timer__gte=timezone.now() - timezone.timedelta(
                days=settings.PERIOD_BLOCK_MENU_ITEM_OUT_OF_STOCK)).exists()

    def events(self, from_date, to_date, entity_id):
        """
        Get list of out of stock reports for business for the specific period
        """
        query = self.filter(menu_item__business_location__business_id=entity_id)
        if from_date:
            query = query.filter(start_timer__gte=from_date)

        if to_date:
            query = query.filter(start_timer__lte=to_date)

        return query

    def group_by_day(self):
        return self\
            .extra(select={'day': 'to_char( start_timer,  \'YYYY-MM-DD\' )'}) \
            .values('day') \
            .annotate(count=models.Count('start_timer')) \
            .order_by('day')


class UserFavoriteLocationQuerySet(models.QuerySet):

    def get_user_favorites(self, user):
        return self.filter(created_by=user).order_by('-created_date')
