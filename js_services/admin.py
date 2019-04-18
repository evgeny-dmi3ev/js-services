# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import copy
from aldryn_apphooks_config.admin import BaseAppHookConfig, ModelAppHookConfig
from aldryn_people.models import Person
from aldryn_translation_tools.admin import AllTranslationsMixin
from cms.admin.placeholderadmin import FrontendEditableAdminMixin
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.forms import widgets
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm
from sortedm2m_filter_horizontal_widget.forms import SortedFilteredSelectMultiple

from . import models

from .constants import (
    SERVICES_SUMMARY_RICHTEXT,
    SERVICES_HIDE_RELATED_SERVICES,
    SERVICES_ENABLE_PUBDATE,
    SERVICES_ENABLE_IMAGE,
)

from cms.admin.placeholderadmin import PlaceholderAdminMixin


def make_published(modeladmin, request, queryset):
    queryset.update(is_published=True)


make_published.short_description = _(
    "Mark selected articles as published")


def make_unpublished(modeladmin, request, queryset):
    queryset.update(is_published=False)


make_unpublished.short_description = _(
    "Mark selected articles as not published")


def make_featured(modeladmin, request, queryset):
    queryset.update(is_featured=True)


make_featured.short_description = _(
    "Mark selected articles as featured")


def make_not_featured(modeladmin, request, queryset):
    queryset.update(is_featured=False)


make_not_featured.short_description = _(
    "Mark selected articles as not featured")


class ServiceAdminForm(TranslatableModelForm):

    class Meta:
        model = models.Service
        fields = [
            'categories',
            'companies',
            'featured_image',
            'is_featured',
            'is_published',
            'lead_in',
            'meta_description',
            'meta_keywords',
            'meta_title',
            'sections',
            'slug',
            'related',
            'title',
        ]

    def __init__(self, *args, **kwargs):
        super(ServiceAdminForm, self).__init__(*args, **kwargs)

        qs = models.Service.objects
        #if self.instance.app_config_id:
            #qs = models.Service.objects.filter(
                #app_config=self.instance.app_config)
        #elif 'initial' in kwargs and 'app_config' in kwargs['initial']:
            #qs = models.Service.objects.filter(
                #app_config=kwargs['initial']['app_config'])

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if 'related' in self.fields:
            self.fields['related'].queryset = qs

        # Don't allow app_configs to be added here. The correct way to add an
        # apphook-config is to create an apphook on a cms Page.
        #self.fields['app_config'].widget.can_add_related = False
        # Don't allow related articles to be added here.
        # doesn't makes much sense to add articles from another article other
        # than save and add another.
        if ('related' in self.fields and
                hasattr(self.fields['related'], 'widget')):
            self.fields['related'].widget.can_add_related = False
        if not SERVICES_SUMMARY_RICHTEXT:
            self.fields['lead_in'].widget = widgets.Textarea()
        self.fields['lead_in'].help_text = """The Summary gives the reader
         the main idea of the service, this is useful in overviews, lists or
         as an introduction to your service."""


class ServiceAdmin(
    AllTranslationsMixin,
    PlaceholderAdminMixin,
    FrontendEditableAdminMixin,
    ModelAppHookConfig,
    TranslatableAdmin
):
    app_config_attribute = 'sections'
    form = ServiceAdminForm
    list_display = ('title', 'slug', 'is_featured',
                    'is_published')
    list_filter = [
        'sections',
        'categories',
        'companies',
    ]
    actions = (
        make_featured, make_not_featured,
        make_published, make_unpublished,
    )


    settings_fields = (
        'title',
        'is_published',
        'is_featured',
    )
    if SERVICES_ENABLE_PUBDATE:
        settings_fields += (
            'publishing_date',
        )
    if SERVICES_ENABLE_IMAGE:
        settings_fields += (
            'featured_image',
        )
    settings_fields += (
        'lead_in',
    )


    advanced_settings_fields = (
        'categories',
    )
    if SERVICES_HIDE_RELATED_SERVICES == 0:
        advanced_settings_fields += (
            'related',
        )

    advanced_settings_fields += (
        'companies',
        'sections',
    )

    fieldsets = (
        (None, {
            'fields': settings_fields
        }),
        (_('Categorisation'), {
            'classes': ('collapse',),
            'fields': advanced_settings_fields,
        }),
        (_('Meta Options'), {
            'classes': ('collapse',),
            'fields': (
                'slug',
                'meta_title',
                'meta_description',
                'meta_keywords',
            )
        }),
    )



    filter_horizontal = [
        'categories',
        'sections',
    ]
    app_config_values = {
        'default_published': 'is_published'
    }
    app_config_selection_title = ''
    app_config_selection_desc = ''

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'related' and SERVICES_HIDE_RELATED_SERVICES == 0:
            kwargs['widget'] = SortedFilteredSelectMultiple(attrs={'verbose_name': 'service', 'verbose_name_plural': 'related services'})
        if db_field.name == 'companies':
            kwargs['widget'] = SortedFilteredSelectMultiple(attrs={'verbose_name': 'company', 'verbose_name_plural': 'companies'})
        if db_field.name == 'sections':
            kwargs["queryset"] = models.ServicesConfig.objects.exclude(namespace=models.ServicesConfig.default_namespace)
        return super(ServiceAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        return super(TranslatableAdmin, self).get_form(request, obj, **kwargs)

admin.site.register(models.Service, ServiceAdmin)


class ServicesConfigAdmin(
    AllTranslationsMixin,
    PlaceholderAdminMixin,
    BaseAppHookConfig,
    TranslatableAdmin
):
    def get_config_fields(self):
        return (
            'app_title', 'permalink_type', 'non_permalink_handling',
            'template_prefix', 'paginate_by', 'pagination_pages_start',
            'pagination_pages_visible', 'exclude_featured',
            'search_indexed', 'config.default_published',)

    #def get_readonly_fields(self, request, obj=None):
        #return self.readonly_fields

admin.site.register(models.ServicesConfig, ServicesConfigAdmin)
