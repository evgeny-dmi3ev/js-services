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
