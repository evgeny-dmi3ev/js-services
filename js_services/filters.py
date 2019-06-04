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
    IS_THERE_COMPANIES,
    ADD_FILTERED_CATEGORIES,
)
if IS_THERE_COMPANIES:
    from js_companies.models import Company



class ServiceFilters(django_filters.FilterSet):
    q = django_filters.CharFilter('translations__title', 'icontains', label='Search the directory')
    category = django_filters.ModelChoiceFilter('categories', label='category', queryset=Category.objects.all().order_by('translations__name'))
    section = django_filters.ModelChoiceFilter('sections', label='section', queryset=ServicesConfig.objects.all().order_by('translations__app_title'))
    letter = django_filters.CharFilter('translations__title', 'istartswith')

    class Meta:
        model = models.Service
        fields = ['q', 'category', 'section', 'letter']

    def __init__(self, values, *args, **kwargs):
        super(ServiceFilters, self).__init__(values, *args, **kwargs)
        self.filters['category'].extra.update({'empty_label': 'by category'})
        self.filters['section'].extra.update({'empty_label': 'by section'})
        if IS_THERE_COMPANIES:
            self.filters['company'] = django_filters.ModelChoiceFilter('companies', label='company', queryset=Company.objects.all().order_by('name'))
            self.filters['company'].extra.update({'empty_label': 'by company'})
        if ADD_FILTERED_CATEGORIES:
            for category in ADD_FILTERED_CATEGORIES:
                qs = Category.objects.filter(translations__slug=category[0])[0].get_children().order_by('translations__name') if Category.objects.filter(translations__slug=category[0]).exists() else Category.objects.none()
                name = category[0].replace('-', '_')
                self.filters[name] = django_filters.ModelChoiceFilter('categories', label=category[1], queryset=qs)
                self.filters[name].extra.update({'empty_label': category[1]})
