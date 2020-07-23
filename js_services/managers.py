# -*- coding: utf-8 -*-

from __future__ import unicode_literals

try:
    from collections import Counter
except ImportError:
    from backport_collections import Counter

import datetime
from operator import attrgetter

from django.db import models
from django.utils.timezone import now

from aldryn_apphooks_config.managers.base import ManagerMixin, QuerySetMixin
from parler.managers import TranslatableManager, TranslatableQuerySet

from .constants import SERVICES_ENABLE_PUBDATE, SERVICES_ENABLE_IMAGE, TRANSLATE_IS_PUBLISHED

class ServiceQuerySet(TranslatableQuerySet):
    def published(self):
        """
        Returns Services that are published AND have a publishing_date that
        has actually passed.
        """
        qs = self
        if SERVICES_ENABLE_PUBDATE:
            qs = self.filter(publishing_date__lte=now())
        if TRANSLATE_IS_PUBLISHED:
            return qs.translated(is_published_trans=True)
        return qs.filter(is_published=True)

    def published_one_of_trans(self):
        qs = self
        if SERVICES_ENABLE_PUBDATE:
            qs = self.filter(publishing_date__lte=now())
        if TRANSLATE_IS_PUBLISHED:
            return qs.filter(translations__is_published_trans=True)
        return qs.filter(is_published=True)


    def namespace(self, namespace, to=None):
        return self.filter(**{'sections__namespace': namespace})


class RelatedManager(ManagerMixin, TranslatableManager):
    def get_queryset(self):
        qs = ServiceQuerySet(self.model, using=self.db)
        if SERVICES_ENABLE_IMAGE:
            return qs.select_related('featured_image')
        return qs

    def published(self):
        return self.get_queryset().published()

    def published_one_of_trans(self):
        return self.get_queryset().published_one_of_trans()

    def get_months(self, request, namespace):
        """
        Get months and years with Services count for given request and namespace
        string. This means how many Services there are in each month.

        The request is required, because logged-in content managers may get
        different counts.

        Return list of dictionaries ordered by Service publishing date of the
        following format:
        [
            {
                'date': date(YEAR, MONTH, ARBITRARY_DAY),
                'num_services': NUM_SERVICES
            },
            ...
        ]
        """

        # TODO: check if this limitation still exists in Django 1.6+
        # This is done in a naive way as Django is having tough time while
        # aggregating on date fields
        if (request and hasattr(request, 'toolbar') and
                request.toolbar and request.toolbar.edit_mode_active):
            services = self.namespace(namespace)
        else:
            services = self.published().namespace(namespace)
        dates = services.values_list('publishing_date', flat=True)
        dates = [(x.year, x.month) for x in dates]
        date_counter = Counter(dates)
        dates = set(dates)
        dates = sorted(dates, reverse=True)
        months = [
            # Use day=3 to make sure timezone won't affect this hacks'
            # month value. There are UTC+14 and UTC-12 timezones!
            {'date': datetime.date(year=year, month=month, day=3),
             'num_services': date_counter[(year, month)]}
            for year, month in dates]
        return months
