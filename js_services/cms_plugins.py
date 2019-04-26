# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from django.template import TemplateDoesNotExist
from django.template.loader import select_template
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from js_services import models, forms


@plugin_pool.register_plugin
class RelatedServicesPlugin(CMSPluginBase):
    TEMPLATE_NAME = 'js_services/plugins/related_services__%s.html'
    module = 'Services'
    render_template = 'js_services/plugins/related_services.html'
    name = _('Related Services')
    model = models.RelatedServicesPlugin
    form = forms.RelatedServicesPluginForm

    def render(self, context, instance, placeholder):
        request = context.get('request')
        context['instance'] = instance
        context['title'] = instance.title
        context['icon'] = instance.icon
        context['image'] = instance.image

        qs = instance.related_services.published()
        related_sections = instance.related_sections.all()
        related_people = instance.related_people.all()
        related_companies = instance.related_companies.all()
        related_categories = instance.related_categories.all()

        if not qs.exists():
            qs = models.Service.objects.published().distinct()
            if related_sections.exists():
                qs = qs.filter(sections=related_sections)
            if related_people.exists():
                qs = qs.filter(person_set=related_people)
            if related_companies.exists():
                qs = qs.filter(companies=related_companies)
            if related_categories.exists():
                qs = qs.filter(services__in=related_categories)

        context['related_services'] = qs[:int(instance.count)]

        return context

    def get_render_template(self, context, instance, placeholder):
        if instance.layout:
            template = self.TEMPLATE_NAME % instance.layout
            try:
                select_template([template])
                return template
            except TemplateDoesNotExist:
                pass
        return self.render_template
