# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.widgets import AdminTimeWidget
from django.utils import timezone
from django.utils.safestring import mark_safe
from tinymce.widgets import TinyMCE

from web.businesses.api.services import BusinessLocationService
from web.businesses.es_service import BusinessLocationESService
from web.businesses.models import Business, BusinessLocation, FeaturedBusinessLocation, \
    LocationReview, State, City, Payment, GrowerDispensaryPartnership, BusinessLocationMenuUpdate, \
    BusinessLocationMenuItem, BusinessLocationMenuUpdateRequest, ReportOutOfStock


class PaymentInline(admin.TabularInline):
    extra = 0
    model = Payment
    ordering = ('-date',)


class BusinessLocationInline(admin.TabularInline):
    extra = 0
    model = BusinessLocation
    fields = ('location_name', 'location_email', 'dispensary', 'delivery', 'grow_house', 'delivery_radius',
              'phone', 'verified', 'removed_date')
    show_change_link = True
    view_on_site = False

    def has_add_permission(self, request, obj=None):
        return False


class MenuInline(admin.TabularInline):
    extra = 0
    model = BusinessLocationMenuItem


def enable_business_search(modeladmin, request, queryset):
    for business in queryset:
        business.is_searchable = True
        business.save()

    es_service = BusinessLocationESService()
    for location in BusinessLocation.objects.filter(business__in=queryset):
        es_service.save_business_location(location)


enable_business_search.short_description = 'Enable search'


def disable_business_search(modeladmin, request, queryset):
    for business in queryset:
        business.is_searchable = False
        business.save()

    es_service = BusinessLocationESService()
    for location in BusinessLocation.objects.filter(business__in=queryset):
        es_service.save_business_location(location)


disable_business_search.short_description = 'Disable search'


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'is_searchable', 'account_type', 'last_payment_date', 'last_payment_amount')
    list_filter = ('account_type', 'is_active', 'is_searchable')
    search_fields = ('name',)
    readonly_fields = ('last_payment_date', 'last_payment_amount')
    inlines = (PaymentInline, BusinessLocationInline)
    actions = [enable_business_search, disable_business_search]


def activate_selected_locations(modeladmin, request, queryset):
    for l in queryset:
        l.removed_by = None
        l.removed_date = None
        l.save()


activate_selected_locations.short_description = 'Activate selected'


def deactivate_selected_locations(modeladmin, request, queryset):
    service = BusinessLocationService()
    for l in queryset:
        service.remove_location(l.id, request.user.id)


deactivate_selected_locations.short_description = 'Deactivate selected'


def verify_email_for_selected_locations(modeladmin, request, queryset):
    for l in queryset:
        location_creator = l.business.created_by
        is_verified = location_creator.is_email_verified

        if not is_verified:
            location_creator.is_email_verified = True
            location_creator.save()


verify_email_for_selected_locations.short_description = 'Verify email'


class BusinessLocationAdminForm(forms.ModelForm):
    class Meta:
        model = BusinessLocation
        fields = '__all__'

    about = forms.Textarea()
    location_field = forms.CharField(max_length=255)
    
    mon_open = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    mon_close = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    tue_open = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    tue_close = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    wed_open = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    wed_close = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    thu_open = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    thu_close = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    fri_open = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    fri_close = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    sat_open = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    sat_close = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    sun_open = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)
    sun_close = forms.TimeField(widget=AdminTimeWidget(format='%I:%M %p'), input_formats=('%I:%M %p',), required=False)

    def __init__(self, *args, **kwargs):
        super(BusinessLocationAdminForm, self).__init__(*args, **kwargs)

        self.fields['location_email'].required = True
        self.fields['phone'].required = True
        self.fields['location_field'].required = True


class OwnerEmailVerifiedFilter(SimpleListFilter):
    title = 'Owner Email Verified'
    parameter_name = 'owner_email_verified'

    def lookups(self, request, model_admin):
        return [('verified', 'Verified'), ('not_verified', 'Not Verified')]

    def queryset(self, request, queryset):
        if self.value():
            is_verified = self.value() == 'verified'
            return queryset.filter(business__created_by__is_email_verified=is_verified)


class ActivityFilter(SimpleListFilter):
    title = 'Activeness'
    parameter_name = 'removed_date'

    def lookups(self, request, model_admin):
        return [('active', 'Active'), ('deactivated', 'Deactivated')]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset

        return queryset.filter(removed_date__isnull=(self.value() == 'active'))


def stop_featuring(modeladmin, request, queryset):
    queryset.delete()


stop_featuring.short_description = 'Stop Featuring'


@admin.register(FeaturedBusinessLocation)
class FeaturedBusinessLocationAdmin(admin.ModelAdmin):
    list_display = ['business_location', 'zip_code', 'featured_datetime']
    search_fields = ('business_location', 'zip_code')
    actions = [stop_featuring]


class FeaturedBusinessLocationInline(admin.TabularInline):
    extra = 0
    fields = ['zip_code']
    readonly_fields = ['featured_datetime']
    model = FeaturedBusinessLocation


class BusinessLocationMenuUpdateInline(admin.TabularInline):
    extra = 0
    fields = ['date']
    readonly_fields = ['date']
    model = BusinessLocationMenuUpdate
    max_num = 0


@admin.register(BusinessLocation)
class BusinessLocationAdmin(admin.ModelAdmin):
    change_form_template = 'admin/business/business_location_change_form.html'
    form = BusinessLocationAdminForm

    fieldsets = (
        ('Info',
         {'fields': ('business', 'verified', 'form_url', 'removed_date', 'location_name', 'manager_name', 'location_email', 'phone', 'ext', 'about',), }),
        ('Social',
         {'fields': ('meta_desc', 'meta_keywords', 'social_image'), }),
        ('Type',
         {'fields': ('dispensary', 'grow_house', 'delivery', 'delivery_radius', 'grow_details'), }),
        ('Location',
         {'fields': ('location_field', 'street1', 'city', 'state', 'zip_code', 'lat', 'lng', 'location_raw',), }),
        ('Working Hours',
         {'fields': ('mon_open', 'mon_close', 'tue_open', 'tue_close', 'wed_open', 'wed_close', 'thu_open', 'thu_close',
                     'fri_open', 'fri_close', 'sat_open', 'sat_close', 'sun_open', 'sun_close',), }),
        ('Menu',
         {'fields': ('menu_updated_date',)}),
    )

    def form_url(self, instance):
        return mark_safe('<a target="_blank" href="{url}">{url}</a>'.format(url=instance.url))

    list_display = ['business', 'location_name', 'dispensary', 'delivery', 'grow_house',
                    'created_date', 'removed_date', 'owner_email_verified']
    readonly_fields = ['category', 'slug_name', 'primary', 'form_url']
    search_fields = ['location_name']
    list_filter = [OwnerEmailVerifiedFilter, ActivityFilter, 'dispensary', 'delivery', 'grow_house']
    ordering = ['location_name']
    actions = [activate_selected_locations, deactivate_selected_locations, verify_email_for_selected_locations]
    inlines = (BusinessLocationMenuUpdateInline, FeaturedBusinessLocationInline, MenuInline)

    @staticmethod
    def owner_email_verified(obj):
        return obj.business.created_by.is_email_verified


def approve_selected_ratings(modeladmin, request, queryset):
    for rating in queryset:
        rating.review_approved = True
        rating.last_modified_by = request.user
        rating.save()


approve_selected_ratings.short_description = 'Approve selected ratings'


@admin.register(LocationReview)
class LocationReviewAdmin(admin.ModelAdmin):
    list_display = ['location', 'rating', 'review', 'review_approved', 'created_date', 'created_by']
    search_fields = ['location__name', 'rating', 'review_approved', 'created_date',
                     'created_by__email', 'created_by__first_name', 'created_by__last_name']
    list_filter = ['rating', 'review_approved', 'created_date', 'last_modified_date']
    ordering = ['-created_date']
    readonly_fields = ['location', 'rating', 'review', 'created_date', 'created_by',
                       'last_modified_date', 'last_modified_by']
    actions = [approve_selected_ratings]


class StateAdminForm(forms.ModelForm):
    class Meta:
        model = State
        fields = '__all__'

    description = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 20}),
                                  help_text='This will be used on /dispensaries page as a state description')
    description2 = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 20}),
                                   help_text='This will be used on /dispensaries/{state} page as a state description')


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    form = StateAdminForm

    list_display = ['abbreviation', 'full_name']
    search_fields = ['abbreviation', 'full_name']
    list_filter = ['abbreviation', 'full_name']
    ordering = ['abbreviation']


class CityAdminForm(forms.ModelForm):
    class Meta:
        model = City
        fields = '__all__'

    description = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 20}), required=False)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    form = CityAdminForm

    list_display = ['full_name', 'state', 'description']
    search_fields = ['state__abbreviation', 'full_name']
    list_filter = ['state__abbreviation', 'full_name']
    ordering = ['full_name']
    readonly_fields = ['full_name_slug']


class GrowerDispensaryPartnershipForm(forms.ModelForm):
    class Meta:
        model = GrowerDispensaryPartnership
        fields = ('grower', 'dispensary')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['grower'].queryset = BusinessLocation.objects.filter(grow_house=True)
        self.fields['dispensary'].queryset = BusinessLocation.objects.filter(dispensary=True)


@admin.register(GrowerDispensaryPartnership)
class GrowerDispensaryPartnershipAdmin(admin.ModelAdmin):
    form = GrowerDispensaryPartnershipForm

    list_display = ('grower', 'dispensary')
    search_fields = ('grower', 'dispensary')


admin.site.register(BusinessLocationMenuUpdateRequest)
admin.site.register(BusinessLocationMenuItem)


@admin.register(ReportOutOfStock)
class ReportOutOfStockAdmin(admin.ModelAdmin):
    list_display = ('business_location', 'vt', 'user', 'start_timer', 'countdown', 'count')
    list_select_related = ('menu_item__business_location', 'menu_item__vt')
    readonly_fields = ('count',)

    def business_location(self, instance):
        return instance.menu_item.business_location.location_name

    def vt(self, instance):
        return instance.menu_item.vt.name

    def countdown(self, instance):
        delta = timezone.now() - instance.start_timer
        if not instance.is_active:
            return
        if instance.count >= 2 and delta.days < settings.PERIOD_BLOCK_MENU_ITEM_OUT_OF_STOCK:
            return timezone.timedelta(days=settings.PERIOD_BLOCK_MENU_ITEM_OUT_OF_STOCK) - delta
        elif instance.count == 1 and delta.days < settings.PERIOD_OUT_OF_STOCK:
            return timezone.timedelta(days=settings.PERIOD_OUT_OF_STOCK) - delta
