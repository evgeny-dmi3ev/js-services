# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from functools import reduce
from django.db.models import Q
from django import forms
from aldryn_categories.models import Category
import django_filters
from . import models
from .cms_appconfig import ServicesConfig
from .constants import (
    UPDATE_SEARCH_DATA_ON_SAVE,
    IS_THERE_COMPANIES,
    ADD_FILTERED_CATEGORIES,
    ADDITIONAL_EXCLUDE,
    FILTER_EMPTY_LABELS,
)
if IS_THERE_COMPANIES:
    from js_companies.models import Company

try:
    from custom.js_services.filters import CustomFilterMixin
except:
    class CustomFilterMixin(object):
        pass

class SearchFilter(django_filters.Filter):
    def filter(self, qs, values):
        values = values or ''
        if len(values) > 0:
            for value in values.strip().split():
                value = value.strip()
                if value:
                    qs = qs.filter(translations__search_data__icontains=value)
        return qs



class ServiceFilters(CustomFilterMixin, django_filters.FilterSet):
    q = django_filters.CharFilter('translations__title', 'icontains', label='Search the directory')
    service = django_filters.ModelChoiceFilter('related', label='service', empty_label='by service', queryset=models.Service.objects.published().exclude(**ADDITIONAL_EXCLUDE.get('service', {})))
    category = django_filters.ModelChoiceFilter('categories', label='category', empty_label='by category', queryset=Category.objects.exclude(**ADDITIONAL_EXCLUDE.get('category', {})))
    section = django_filters.ModelChoiceFilter('sections', label='section', empty_label='by section', queryset=ServicesConfig.objects.exclude(namespace=ServicesConfig.default_namespace).exclude(**ADDITIONAL_EXCLUDE.get('section', {})))
    letter = django_filters.CharFilter('translations__title', 'istartswith')

    class Meta:
        model = models.Service
        fields = ['q', 'category', 'section', 'letter']

    def __init__(self, values, *args, **kwargs):
        super(ServiceFilters, self).__init__(values, *args, **kwargs)
        if UPDATE_SEARCH_DATA_ON_SAVE:
            self.filters['q'] = SearchFilter(label='Search the directory')
        selects = ['category', 'service', 'section']
        if IS_THERE_COMPANIES:
            self.filters['company'] = django_filters.ModelChoiceFilter('companies', label='company', empty_label='by company', queryset=Company.objects.exclude(**ADDITIONAL_EXCLUDE.get('company', {})).order_by('name'))
            selects.append('company')
        if ADD_FILTERED_CATEGORIES:
            for category in ADD_FILTERED_CATEGORIES:
                qs = Category.objects.filter(translations__slug=category[0])[0].get_children().exclude(**ADDITIONAL_EXCLUDE.get(category[0], {})).order_by('translations__name') if Category.objects.filter(translations__slug=category[0]).exists() else Category.objects.none()
                name = category[0].replace('-', '_')
                self.filters[name] = django_filters.ModelChoiceFilter('categories', label=category[1], queryset=qs)
                self.filters[name].extra.update({'empty_label': 'by %s' % category[1]})
                selects.append(name)

        self.set_empty_labels(**FILTER_EMPTY_LABELS)

        for field in selects:
            self.sort_choices(self.filters[field])

    def set_empty_labels(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.filters:
                self.filters[key].extra['empty_label'] = value

    def sort_choices(self, field):
        field = field.field
        if isinstance(field.choices, django_filters.fields.ModelChoiceIterator):
            choices = [(obj.pk, str(obj)) for obj in field.choices.queryset]
            field.iterator = django_filters.fields.ChoiceIterator
            field._set_choices(sorted(choices, key=lambda item: item[1]))
