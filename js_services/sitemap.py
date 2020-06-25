# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from aldryn_translation_tools.sitemaps import I18NSitemap

from .models import Service
from .cms_appconfig import ServicesConfig
from .constants import SITEMAP_CHANGEFREQ, SITEMAP_PRIORITY


class ServicesSitemap(I18NSitemap):

    changefreq = SITEMAP_CHANGEFREQ
    priority = SITEMAP_PRIORITY

    def __init__(self, *args, **kwargs):
        self.namespace = kwargs.pop('namespace', None)
        if self.namespace == ServicesConfig.default_namespace:
            self.namespace = None
        self.sitemap_type = kwargs.pop('type', 'xml')
        super(ServicesSitemap, self).__init__(*args, **kwargs)

    def items(self):
        qs = Service.objects.published()
        if self.language is not None:
            qs = qs.language(self.language)
        if self.namespace is not None:
            qs = qs.filter(sections__namespace=self.namespace)
        if self.sitemap_type == 'html':
            qs = qs.exclude(show_on_sitemap=False)
        elif self.sitemap_type == 'xml':
            qs = qs.exclude(show_on_xml_sitemap=False)
        return qs

    def lastmod(self, obj):
        return obj.publishing_date
