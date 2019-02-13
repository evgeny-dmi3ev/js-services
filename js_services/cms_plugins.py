# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from .models import Service


@plugin_pool.register_plugin
class ServicePlugin(CMSPluginBase):
    model = Service
    name = _('Jumpsuite Services')
    admin_preview = False
    render_template = 'js_services/js_services.html'

    def render(self, context, instance, placeholder):
        context.update({
            'object': instance,
            'placeholder': placeholder,
        })
        return context
