# -*- coding: utf-8 -*-

from django.conf import settings

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
ADD_FILTERED_CATEGORIES = getattr(
    settings,
    'SERVICES_ADD_FILTERED_CATEGORIES',
    [],
)
SERVICES_GROUP_BY_SECTIONS = getattr(
    settings,
    'SERVICES_GROUP_BY_SECTIONS',
    False,
)

try:
    IS_THERE_COMPANIES = True
    from js_companies.models import Company
except:
    IS_THERE_COMPANIES = False
