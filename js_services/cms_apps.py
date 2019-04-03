# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from aldryn_apphooks_config.app_base import CMSConfigApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _

from .models import ServicesConfig


class ServicesApp(CMSConfigApp):
    name = _('Services')
    app_name = 'js_services'
    app_config = ServicesConfig

    def get_urls(self, *args, **kwargs):
        return ['js_services.urls']

    def get_configs(self):
        if not self.app_config.objects.filter(namespace=self.app_config.default_namespace).exists():
            conf = self.app_config(namespace=self.app_config.default_namespace, app_title=self.app_config.default_app_title)
            conf.save()
        return self.app_config.objects.all()


apphook_pool.register(ServicesApp)
