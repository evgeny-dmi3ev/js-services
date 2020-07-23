# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
try:
    from django.core.urlresolvers import reverse, NoReverseMatch
except ImportError:
    # Django 2.0
    from django.urls import reverse, NoReverseMatch
from django.utils.translation import (
    ugettext as _, get_language_from_request, override)

from cms.api import get_page_draft
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from cms.cms_toolbars import LANGUAGE_MENU_IDENTIFIER
from cms.utils.i18n import get_language_tuple, get_language_dict
from menus.utils import DefaultLanguageChanger

from aldryn_apphooks_config.utils import get_app_instance
from aldryn_translation_tools.utils import (
    get_object_from_request,
    get_admin_url,
)

from .models import Service
from .cms_appconfig import ServicesConfig

from cms.cms_toolbars import ADMIN_MENU_IDENTIFIER, ADMINISTRATION_BREAK

ADD_OBJ_LANGUAGE_BREAK = "Add object language Break"

@toolbar_pool.register
class ServicesToolbar(CMSToolbar):
    # watch_models must be a list, not a tuple
    # see https://github.com/divio/django-cms/issues/4135
    watch_models = [Service, ]
    supported_apps = ('js_services',)

    def get_on_delete_redirect_url(self, obj, language):
        with override(language):
            url = reverse(
                '{0}:service-list'.format(obj.app_config.namespace))
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
        self.page = get_page_draft(self.request.current_page)
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
                obj = get_object_from_request(Service, self.request)
            else:
                obj = None

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

            if change_service_perm and obj:
                url_args = {}
                if language:
                    url_args = {'language': language, }
                url = get_admin_url('js_services_service_change',
                                    [obj.pk, ], **url_args)
                menu.add_modal_item(_('Edit this service'), url=url,
                                    active=True)

            if delete_service_perm and obj:
                redirect_url = self.get_on_delete_redirect_url(
                    obj, language=language)
                url = get_admin_url('js_services_service_delete',
                                    [obj.pk, ])
                menu.add_modal_item(_('Delete this service'), url=url,
                                    on_close=redirect_url)

        if settings.USE_I18N:# and not self._language_menu:
            if obj:
                self._language_menu = self.toolbar.get_or_create_menu(LANGUAGE_MENU_IDENTIFIER, _('Language'), position=-1)
                self._language_menu.items = []
                languages = get_language_dict(self.current_site.pk)
                page_languages = self.page.get_languages()
                remove = []

                for code, name in get_language_tuple():
                    if code in obj.get_available_languages():
                        remove.append((code, name))
                        try:
                            url = obj.get_absolute_url(code)
                        except NoReverseMatch:
                            url = None
                        if url and code in page_languages:
                            self._language_menu.add_link_item(name, url=url, active=self.current_lang == code)

                if self.toolbar.edit_mode_active:
                    add = [l for l in languages.items() if l not in remove]
                    copy = [(code, name) for code, name in languages.items() if code != self.current_lang and (code, name) in remove]

                    if (add or len(remove) > 1 or copy) and change_service_perm:
                        self._language_menu.add_break(ADD_OBJ_LANGUAGE_BREAK)

                        if add:
                            add_plugins_menu = self._language_menu.get_or_create_menu('{0}-add-trans'.format(LANGUAGE_MENU_IDENTIFIER), _('Add Translation'))
                            for code, name in add:
                                url_args = {}
                                url = '%s?language=%s' % (get_admin_url('js_services_service_change',
                                    [obj.pk], **url_args), code)
                                add_plugins_menu.add_modal_item(name, url=url)

                        if len(remove) > 1:
                            remove_plugins_menu = self._language_menu.get_or_create_menu('{0}-del-trans'.format(LANGUAGE_MENU_IDENTIFIER), _('Delete Translation'))
                            for code, name in remove:
                                url = get_admin_url('js_services_service_delete_translation', [obj.pk, code])
                                remove_plugins_menu.add_modal_item(name, url=url)

                        if copy:
                            copy_plugins_menu = self._language_menu.get_or_create_menu('{0}-copy-trans'.format(LANGUAGE_MENU_IDENTIFIER), _('Copy all plugins'))
                            title = _('from %s')
                            question = _('Are you sure you want to copy all plugins from %s?')
                            url = get_admin_url('js_services_service_copy_language', [obj.pk])
                            for code, name in copy:
                                copy_plugins_menu.add_ajax_item(
                                    title % name, action=url,
                                    data={'source_language': code, 'target_language': self.current_lang},
                                    question=question % name, on_success=self.toolbar.REFRESH_PAGE
                                )
