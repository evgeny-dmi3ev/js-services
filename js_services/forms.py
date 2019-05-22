# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.text import slugify
from django.utils.safestring import mark_safe
from sortedm2m_filter_horizontal_widget.forms import SortedFilteredSelectMultiple, SortedMultipleChoiceField
from aldryn_categories.models import Category
from aldryn_people.models import Person
from . import models
from .constants import (
    IS_THERE_COMPANIES,
)
if IS_THERE_COMPANIES:
    from js_companies.models import Company

RELATED_LAYOUTS = getattr(
    settings,
    'SERVICES_RELATED_SERVICES_LAYOUTS',
    (),
)

RELATED_LAYOUTS_CHOICES = zip(list(map(lambda s: slugify(s).replace('-', '_'), ('',) + RELATED_LAYOUTS)), ('default',) + RELATED_LAYOUTS)


class RelatedServicesPluginForm(forms.ModelForm):

    layout = forms.ChoiceField(RELATED_LAYOUTS_CHOICES, required=False)

    related_services = SortedMultipleChoiceField(
        label='related services',
        queryset=models.Service.objects.all(),
        required=False,
        widget=SortedFilteredSelectMultiple(attrs={'verbose_name':'service', 'verbose_name_plural':'services'})
    )
    related_sections = forms.ModelMultipleChoiceField(
        queryset=models.ServicesConfig.objects.exclude(namespace=models.ServicesConfig.default_namespace),
        required=False,
        widget=FilteredSelectMultiple('sections', False)
    )
    related_people = forms.ModelMultipleChoiceField(
        queryset=Person.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('people', False)
    )
    related_categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('categories', False)
    )
    related_companies = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(RelatedServicesPluginForm, self).__init__(*args, **kwargs)
        #if len(RELATED_LAYOUTS) == 0:
        #    self.fields['layout'].widget = forms.HiddenInput()
        if IS_THERE_COMPANIES:
            self.fields['related_companies'] = forms.ModelMultipleChoiceField(queryset=Company.objects.all(), required=False)
            self.fields['related_companies'].widget = SortedFilteredSelectMultiple()
            self.fields['related_companies'].queryset = Company.objects.all()
            if self.instance.pk and self.instance.related_companies.count():
                self.fields['related_companies'].initial = self.instance.related_companies.all()
