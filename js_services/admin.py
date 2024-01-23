# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import copy
from aldryn_apphooks_config.admin import BaseAppHookConfig, ModelAppHookConfig
from aldryn_people.models import Person
from aldryn_translation_tools.admin import AllTranslationsMixin
from cms.admin.placeholderadmin import FrontendEditableAdminMixin
from cms.admin.placeholderadmin import PlaceholderAdminMixin
from cms.utils.i18n import get_current_language, get_language_list
from cms.utils import copy_plugins, get_current_site
from django.db import transaction
from django.db.models.query import EmptyQuerySet
from django import forms
from django.conf.urls import url
from django.contrib import admin
from django.contrib.sites.models import Site
from django.forms import widgets
from django.views.decorators.http import require_POST
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.html import mark_safe
from django.core.exceptions import PermissionDenied
from django.http import (
    HttpResponseRedirect,
    HttpResponse,
    Http404,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm
try:
    from sortedm2m_filter_horizontal_widget.forms import SortedFilteredSelectMultiple
except:
    SortedFilteredSelectMultiple = FilteredSelectMultiple
try:
    from js_custom_fields.forms import CustomFieldsFormMixin, CustomFieldsSettingsFormMixin
except:
    class CustomFieldsFormMixin(object):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if 'custom_fields' in self.fields:
                self.fields['custom_fields'].widget = forms.HiddenInput()

    class CustomFieldsSettingsFormMixin(object):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if 'custom_fields_settings' in self.fields:
                self.fields['custom_fields_settings'].widget = forms.HiddenInput()

from . import models

from .constants import (
    SERVICES_SUMMARY_RICHTEXT,
    SERVICES_HIDE_RELATED_SERVICES,
    SERVICES_ENABLE_PUBDATE,
    SERVICES_ENABLE_IMAGE,
    IS_THERE_COMPANIES,
    TRANSLATE_IS_PUBLISHED,
    TRANSLATE_LAYOUT,
    SERVICE_CUSTOM_FIELDS,
    SERVICE_SECTION_CUSTOM_FIELDS,
    SERVICE_LAYOUT_CHOICES,
)
if IS_THERE_COMPANIES:
    from js_companies.models import Company

require_POST = method_decorator(require_POST)


def make_published(modeladmin, request, queryset):
    if TRANSLATE_IS_PUBLISHED:
        for i in queryset.all():
            i.is_published_trans = True
            i.save()
        #language = get_current_language()
        #models.ArticleTranslation.objects.filter(language_code=language, master__in=queryset).update(is_published_trans=True)
    else:
        queryset.update(is_published=True)


make_published.short_description = _(
    "Mark selected services as published")


def make_unpublished(modeladmin, request, queryset):
    if TRANSLATE_IS_PUBLISHED:
        for i in queryset.all():
            i.is_published_trans = False
            i.save()
        #language = get_current_language()
        #models.ArticleTranslation.objects.filter(language_code=language, master__in=queryset).update(is_published_trans=False)
    else:
        queryset.update(is_published=False)


make_unpublished.short_description = _(
    "Mark selected services as not published")


def make_featured(modeladmin, request, queryset):
    if TRANSLATE_IS_PUBLISHED:
        for i in queryset.all():
            i.is_featured_trans = True
            i.save()
        #language = get_current_language()
        #models.ArticleTranslation.objects.filter(language_code=language, master__in=queryset).update(is_featured_trans=True)
    else:
        queryset.update(is_featured=True)


make_featured.short_description = _(
    "Mark selected services as featured")


def make_not_featured(modeladmin, request, queryset):
    if TRANSLATE_IS_PUBLISHED:
        for i in queryset.all():
            i.is_featured_trans = False
            i.save()
        #language = get_current_language()
        #models.ArticleTranslation.objects.filter(language_code=language, master__in=queryset).update(is_featured_trans=False)
    else:
        queryset.update(is_featured=False)


make_not_featured.short_description = _(
    "Mark selected services as not featured")

class ServiceAdminForm(CustomFieldsFormMixin, TranslatableModelForm):
    companies = forms.CharField()
    layout = forms.ChoiceField(choices=SERVICE_LAYOUT_CHOICES, required=False)
    layout_trans = forms.ChoiceField(choices=SERVICE_LAYOUT_CHOICES, required=False)

    custom_fields = 'get_custom_fields'

    class Meta:
        model = models.Service
        fields = '__all__'

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
        if IS_THERE_COMPANIES:
            self.fields['companies'] = forms.ModelMultipleChoiceField(queryset=Company.objects.all(), required=False)# self.instance.companies
            self.fields['companies'].widget = SortedFilteredSelectMultiple()
            self.fields['companies'].queryset = Company.objects.all()
            if self.instance.pk and self.instance.companies.count():
                self.fields['companies'].initial = self.instance.companies.all()
        else:
            del self.fields['companies']

    def get_custom_fields(self):
        fields = SERVICE_CUSTOM_FIELDS
        if self.instance and self.instance.pk:
            for section in self.instance.sections.all():
                if section.custom_fields_settings:
                    fields.update(section.custom_fields_settings)
        return fields



class ServiceAdmin(
    AllTranslationsMixin,
    PlaceholderAdminMixin,
    FrontendEditableAdminMixin,
    #ModelAppHookConfig,
    TranslatableAdmin
):
    search_fields = ['translations__title']
    app_config_attribute = 'sections'
    form = ServiceAdminForm
    list_display = ('title', 'slug', 'is_featured',
                    'is_published')
    list_filter = [
        'is_published',
        'is_featured',
        'sections',
        'categories',
    ]
    if IS_THERE_COMPANIES:
        list_filter += (
            'companies',
        )
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
        'layout',
        'custom_fields',
    )

    advanced_settings_fields = (
        'categories',
    )
    if SERVICES_HIDE_RELATED_SERVICES == 0:
        advanced_settings_fields += (
            'related',
        )

    advanced_settings_fields += (
        'sections',
    )
    if IS_THERE_COMPANIES:
        advanced_settings_fields += (
            'companies',
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
                'show_on_sitemap',
                'show_on_xml_sitemap',
                'noindex',
                'nofollow',
                'canonical_url',
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

    def get_list_display(self, request):
        fields = []
        list_display = super().get_list_display(request)
        for field in list_display:
            if field  in ['is_published', 'is_featured'] and TRANSLATE_IS_PUBLISHED:
                field += '_trans'
            fields.append(field)
        return fields

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        for fieldset in fieldsets:
            if len(fieldset) == 2 and 'fields' in fieldset[1]:
                fields = []
                for field in fieldset[1]['fields']:
                    if field  in ['is_published', 'is_featured'] and TRANSLATE_IS_PUBLISHED:
                        field += '_trans'
                    if field  == 'layout' and TRANSLATE_LAYOUT:
                        field += '_trans'
                    fields.append(field)
                fieldset[1]['fields'] = fields
        return fieldsets

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'related' and SERVICES_HIDE_RELATED_SERVICES == 0:
            kwargs['widget'] = SortedFilteredSelectMultiple('service')
        if db_field.name == 'companies':
            kwargs['widget'] = SortedFilteredSelectMultiple('company', False, attrs={'verbose_name_plural': 'companies'})
        if db_field.name == 'sections':
            kwargs["queryset"] = models.ServicesConfig.objects.exclude(namespace=models.ServicesConfig.default_namespace)
        return super(ServiceAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        return super(TranslatableAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if IS_THERE_COMPANIES:
            obj.companies.set(Company.objects.filter(pk__in=form.cleaned_data.get('companies')))

    def get_site(self, request):
        site_id = request.session.get('cms_admin_site')
        if not site_id:
            return get_current_site()
        try:
            site = Site.objects._get_site_by_id(site_id)
        except Site.DoesNotExist:
            site = get_current_site()
        return site

    def all_translations(self, object):
        return mark_safe(super().all_translations(object))

    @require_POST
    @transaction.atomic
    def copy_language(self, request, obj_id):
        obj = self.get_object(request, object_id=obj_id)
        source_language = request.POST.get('source_language')
        target_language = request.POST.get('target_language')

        if not self.has_change_permission(request, obj=obj):
            raise PermissionDenied

        if obj is None:
            raise Http404

        if not target_language or not target_language in get_language_list(site_id=self.get_site(request).pk):
            return HttpResponseBadRequest(force_text(_("Language must be set to a supported language!")))

        for placeholder in obj.get_placeholders():
            plugins = list(
                placeholder.get_plugins(language=source_language).order_by('path'))
            if not placeholder.has_add_plugins_permission(request.user, plugins):
                return HttpResponseForbidden(force_text(_('You do not have permission to copy these plugins.')))
            copy_plugins.copy_plugins_to(plugins, placeholder, target_language)
        return HttpResponse("ok")

    def get_urls(self):
        urlpatterns = super().get_urls()
        opts = self.model._meta
        info = opts.app_label, opts.model_name
        return [url(
            r'^(.+)/copy_language/$',
            self.admin_site.admin_view(self.copy_language),
            name='{0}_{1}_copy_language'.format(*info)
        )] + urlpatterns

admin.site.register(models.Service, ServiceAdmin)

class ServicesConfigAdminForm(CustomFieldsFormMixin, CustomFieldsSettingsFormMixin, TranslatableModelForm):
    custom_fields = SERVICE_SECTION_CUSTOM_FIELDS

class ServicesConfigAdmin(
    AllTranslationsMixin,
    PlaceholderAdminMixin,
    BaseAppHookConfig,
    TranslatableAdmin
):
    form = ServicesConfigAdminForm

    def get_config_fields(self):
        return (
            'app_title', 'allow_post', 'is_featured', 
            'permalink_type', 'non_permalink_handling',
            'template_prefix', 'paginate_by', 'pagination_pages_start',
            'pagination_pages_visible', 'exclude_featured',
            'search_indexed', 'config.default_published',
            'custom_fields_settings', 'custom_fields')

    #def get_readonly_fields(self, request, obj=None):
        #return self.readonly_fields

    def all_translations(self, object):
        return mark_safe(super().all_translations(object))


admin.site.register(models.ServicesConfig, ServicesConfigAdmin)
