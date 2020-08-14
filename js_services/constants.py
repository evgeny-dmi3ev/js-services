# -*- coding: utf-8 -*-

from django.conf import settings

UPDATE_SEARCH_DATA_ON_SAVE = getattr(
    settings,
    'SERVICES_UPDATE_SEARCH_DATA_ON_SAVE',
    False,
)
SERVICES_HIDE_RELATED_SERVICES = getattr(
    settings,
    'SERVICES_HIDE_RELATED_SERVICES',
    False,
)
SERVICES_SUMMARY_RICHTEXT = getattr(
    settings,
    'SERVICES_SUMMARY_RICHTEXT',
    False,
)
SERVICES_ENABLE_PUBDATE = getattr(
    settings,
    'SERVICES_ENABLE_PUBDATE',
    False,
)
SERVICES_ENABLE_IMAGE = getattr(
    settings,
    'SERVICES_ENABLE_IMAGE',
    True,
)
TRANSLATE_IS_PUBLISHED = getattr(
    settings,
    'SERVICES_TRANSLATE_IS_PUBLISHED',
    False,
)
ADD_FILTERED_CATEGORIES = getattr(
    settings,
    'SERVICES_ADD_FILTERED_CATEGORIES',
    [],
)
ADDITIONAL_EXCLUDE = getattr(
    settings,
    'SERVICES_ADDITIONAL_EXCLUDE',
    {},
)
SERVICES_GROUP_BY_SECTIONS = getattr(
    settings,
    'SERVICES_GROUP_BY_SECTIONS',
    False,
)
SERVICES_GET_NEXT_SERVICE = getattr(
    settings,
    'SERVICES_GET_NEXT_SERVICE',
    False,
)
SITEMAP_CHANGEFREQ = getattr(
    settings,
    'SERVICES_SITEMAP_CHANGEFREQ',
    'never',
)
SITEMAP_PRIORITY = getattr(
    settings,
    'SERVICES_SITEMAP_PRIORITY',
    0.5,
)
SERVICE_CUSTOM_FIELDS = getattr(
    settings,
    'SERVICES_SERVICE_CUSTOM_FIELDS',
    {},
)
SERVICE_SECTION_CUSTOM_FIELDS = getattr(
    settings,
    'SERVICES_SERVICE_SECTION_CUSTOM_FIELDS',
    {},
)
try:
    IS_THERE_COMPANIES = True
    from js_companies.models import Company
except:
    IS_THERE_COMPANIES = False
