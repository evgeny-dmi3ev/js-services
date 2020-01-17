# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
try:
    from django.core.urlresolvers import reverse
except ImportError:
    # Django 2.0
    from django.urls import reverse
from django.utils.translation import (
    ugettext as _, get_language_from_request, override)

from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool

from aldryn_apphooks_config.utils import get_app_instance
from aldryn_translation_tools.utils import (
    get_object_from_request,
    get_admin_url,
)

from .models import Service
from .cms_appconfig import ServicesConfig

from cms.cms_toolbars import ADMIN_MENU_IDENTIFIER, ADMINISTRATION_BREAK


@toolbar_pool.register
class ServicesToolbar(CMSToolbar):
    # watch_models must be a list, not a tuple
    # see https://github.com/divio/django-cms/issues/4135
    watch_models = [Service, ]
    supported_apps = ('js_services',)

    def get_on_delete_redirect_url(self, service, language):
        with override(language):
            url = reverse(
                '{0}:service-list'.format(service.app_config.namespace))
        return url

    def __get_services_config(self):
        try:
            __, config = get_app_instance(self.request)
            if not isinstance(config, ServicesConfig):
                # This is not the app_hook you are looking for.
                return None
        except ImproperlyConfigured:
            # There is no app_hook at all.
            return None

        return config

    def populate(self):
        config = self.__get_services_config()
        if not config:
            # Do nothing if there is no services app_config to work with
            return

        user = getattr(self.request, 'user', None)
        try:
            view_name = self.request.resolver_match.view_name
        except AttributeError:
            view_name = None

        if user and view_name:
            language = get_language_from_request(self.request, check_path=True)


            # get existing admin menu
            admin_menu = self.toolbar.get_or_create_menu(ADMIN_MENU_IDENTIFIER)

            # add new Services item
            admin_menu.add_sideframe_item(_('Services'), url='/admin/js_services/service/', position=0)

            # If we're on an Service detail page, then get the service
            if view_name == '{0}:service-detail'.format(config.namespace):
                service = get_object_from_request(Service, self.request)
            else:
                service = None

            menu = self.toolbar.get_or_create_menu('services-app',
                                                   config.get_app_title())

            change_config_perm = user.has_perm(
                'js_services.change_servicesconfig')
            add_config_perm = user.has_perm(
                'js_services.add_servicesconfig')
            config_perms = [change_config_perm, add_config_perm]

            change_service_perm = user.has_perm(
                'js_services.change_service')
            delete_service_perm = user.has_perm(
                'js_services.delete_service')
            add_service_perm = user.has_perm('js_services.add_service')
            service_perms = [change_service_perm, add_service_perm,
                             delete_service_perm, ]

            if change_config_perm:
                url_args = {}
                if language:
                    url_args = {'language': language, }
                url = get_admin_url('js_services_servicesconfig_change',
                                    [config.pk, ], **url_args)
                menu.add_modal_item(_('Configure addon'), url=url)

            if any(config_perms) and any(service_perms):
                menu.add_break()

            if change_service_perm:
                url_args = {}
                if config:
                    url_args = {'sections__id__exact': config.pk}
                url = get_admin_url('js_services_service_changelist',
                                    **url_args)
                menu.add_sideframe_item(_('Service list'), url=url)

            if add_service_perm:
                url_args = {'sections': config.pk, 'owner': user.pk, }
                if language:
                    url_args.update({'language': language, })
                url = get_admin_url('js_services_service_add', **url_args)
                menu.add_modal_item(_('Add new service'), url=url)

            if change_service_perm and service:
                url_args = {}
                if language:
                    url_args = {'language': language, }
                url = get_admin_url('js_services_service_change',
                                    [service.pk, ], **url_args)
                menu.add_modal_item(_('Edit this service'), url=url,
                                    active=True)

            if delete_service_perm and service:
                redirect_url = self.get_on_delete_redirect_url(
                    service, language=language)
                url = get_admin_url('js_services_service_delete',
                                    [service.pk, ])
                menu.add_modal_item(_('Delete this service'), url=url,
                                    on_close=redirect_url)
