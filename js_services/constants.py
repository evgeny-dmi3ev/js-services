# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.text import slugify

UPDATE_SEARCH_DATA_ON_SAVE = getattr(
    settings,
    'SERVICES_UPDATE_SEARCH_DATA_ON_SAVE',
    False,
)
ADD_CATEGORIES_TO_SEARCH_DATA = getattr(
    settings,
    'SEARCH_ADD_CATEGORIES_TO_SEARCH_DATA',
    True
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
TRANSLATE_LAYOUT = getattr(
    settings,
    'SERVICES_TRANSLATE_LAYOUT',
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
SERVICE_LAYOUTS = getattr(
    settings,
    'SERVICES_SERVICE_LAYOUTS',
    (),
)
SERVICE_LAYOUT_CHOICES = list(SERVICE_LAYOUTS)
if len(SERVICE_LAYOUTS) == 0 or len(SERVICE_LAYOUTS[0]) != 2:
    SERVICE_LAYOUT_CHOICES = zip(list(map(lambda s: slugify(s).replace('-', '_'), ('',) + SERVICE_LAYOUTS)), ('default',) + SERVICE_LAYOUTS)
else:
    SERVICE_LAYOUT_CHOICES.insert(0, ('', 'default'))

FILTER_EMPTY_LABELS = getattr(
    settings,
    'SEARCH_FILTER_EMPTY_LABELS',
    {}
)
FILTER_EMPTY_LABELS.update(getattr(
    settings,
    'SERVICES_FILTER_EMPTY_LABELS',
    {}
))
try:
    IS_THERE_COMPANIES = True
    from js_companies.models import Company
except:
    IS_THERE_COMPANIES = False
