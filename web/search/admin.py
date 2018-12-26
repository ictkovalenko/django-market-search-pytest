# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from tinymce.widgets import TinyMCE

from web.businesses.es_service import BusinessLocationESService
from web.businesses.models import BusinessLocationMenuItem
from web.common.widgets import JSONEditorWidget
from web.search.models import *


def activate_selected_vts(modeladmin, request, queryset):
    for vt in queryset:
        vt.removed_by = None
        vt.removed_date = None
        vt.save()


activate_selected_vts.short_description = 'Activate selected'


def deactivate_selected_vts(modeladmin, request, queryset):
    business_location_es_service = BusinessLocationESService()

    for vt in queryset:
        # Delete vt from locations menu
        if BusinessLocationMenuItem.objects.filter(vt=vt).exists():
            for mi in BusinessLocationMenuItem.objects.filter(vt=vt):
                business_location_es_service.delete_menu_item(mi)
                mi.removed_date = datetime.now()
                mi.save()

        # Delete vt itself
        vt.removed_by = request.user.id
        vt.removed_date = datetime.now()
        vt.save()


deactivate_selected_vts.short_description = 'Deactivate selected'


class VtAdminForm(forms.ModelForm):
    class Meta:
        model = Vt
        fields = '__all__'
        exclude = ['internal_id', 'removed_by', 'removed_date']

    about = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 20}), required=False)
    common_name = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            # Update default flavors with new from Flavor model
            flavor = {item: 0 for item in Flavor.objects.values_list('data_name', flat=True)}
            flavor.update(self.fields['flavor'].initial)
            self.initial['flavor'] = flavor


class VtRemovedFilter(SimpleListFilter):
    title = 'Removed'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [
            ('active', 'Active'),
            ('inactive', 'Inactive')
        ]

    def queryset(self, request, queryset):
        removed_value = self.value()

        if removed_value == 'inactive':
            return queryset.exclude(removed_date=None)
        elif removed_value == 'active':
            return queryset.filter(removed_date=None)

        return queryset.all()


class VtImageInline(admin.TabularInline):
    extra = 0
    model = VtImage


@admin.register(Vt)
class VtAdmin(admin.ModelAdmin):
    form = VtAdminForm
    inlines = (VtImageInline,)
    list_display = ('name', 'category', 'variety', 'removed_date')
    search_fields = ('name', 'category', 'variety')
    list_filter = (VtRemovedFilter, 'category', 'variety', 'name')
    ordering = ('name',)
    actions = (activate_selected_vts, deactivate_selected_vts)
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }


def approve_selected_ratings(modeladmin, request, queryset):
    for rating in queryset:
        rating.review_approved = True
        rating.last_modified_by = request.user
        rating.save()


approve_selected_ratings.short_description = 'Approve selected ratings'


@admin.register(VtReview)
class VtReviewAdmin(admin.ModelAdmin):
    list_display = ['vt', 'rating', 'review_approved', 'created_date', 'created_by']
    search_fields = ['vt__name', 'rating', 'review_approved', 'created_date',
                     'created_by__email', 'created_by__first_name', 'created_by__last_name']
    list_filter = ['rating', 'review_approved', 'created_date', 'last_modified_date']
    ordering = ['-created_date']
    actions = [approve_selected_ratings]
    formfield_overrides = {
        models.CharField: {'widget': forms.Textarea},
    }


def get_client_ip(request):
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        return request.META.get('HTTP_X_FORWARDED_FOR').split(',')[-1].strip()
    elif request.META.get('HTTP_X_REAL_IP'):
        return request.META.get('HTTP_X_REAL_IP')
    else:
        return request.META.get('REMOTE_ADDR')


def remove_user_ratings(modeladmin, request, queryset):
    for review in queryset:
        review.removed_date = datetime.now()
        review.last_modified_ip = get_client_ip(request)
        review.last_modified_by = request.user
        review.last_modified_date = datetime.now()
        review.save()


remove_user_ratings.short_description = 'Soft delete selected user ratings'


@admin.register(VtRating)
class VtRatingAdmin(admin.ModelAdmin):
    list_display = ['vt', 'created_by', 'status', 'created_date', 'removed_date']
    search_fields = ['vt__name', 'created_by__email', 'created_by__first_name', 'created_by__last_name',
                     'status', 'created_date', 'removed_date']
    list_filter = ['vt', 'created_by', 'status', 'created_date', 'removed_date']
    ordering = ['-created_date']
    readonly_fields = ['vt', 'effects', 'effects_changed', 'benefits', 'benefits_changed',
                       'side_effects', 'side_effects_changed', 'status', 'removed_date', 'created_by', 'created_date',
                       'created_by_ip', 'last_modified_date', 'last_modified_by', 'last_modified_by_ip']
    actions = [remove_user_ratings]


def approve_vt_image(modeladmin, request, queryset):
    for image in queryset:
        image.is_approved = True
        image.save()


approve_vt_image.short_description = 'Approve Image'


@admin.register(VtImage)
class VtImageAdmin(admin.ModelAdmin):
    list_display = ['vt', 'created_by', 'is_approved', 'is_primary', 'created_date', 'image']
    search_fields = ['vt__name', 'created_by__email', 'created_by__first_name', 'created_by__last_name',
                     'is_approved']
    list_filter = ['is_approved', 'created_date']
    ordering = ['-created_date']
    readonly_fields = ['vt', 'created_by', 'created_date', 'image']
    actions = [approve_vt_image, 'delete_selected']


@admin.register(Effect)
class EffectAdmin(admin.ModelAdmin):
    pass


@admin.register(Flavor)
class FlavorAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'data_name', 'image']
    search_fields = ['display_name', 'data_name']
    ordering = ['display_name']
    readonly_fields = ['data_name']


@admin.register(UserSearch)
class UserSearchAdmin(admin.ModelAdmin):
    search_fields = ['user__email']
