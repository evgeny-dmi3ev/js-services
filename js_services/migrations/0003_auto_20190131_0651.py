# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-01-31 06:51
from __future__ import unicode_literals

import aldryn_apphooks_config.fields
import app_data.fields
from django.db import migrations, models
import django.db.models.deletion
import parler.models


class Migration(migrations.Migration):

    dependencies = [
        ('js_services', '0002_service_related'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServicesConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=100, verbose_name='Type')),
                ('namespace', models.CharField(default=None, max_length=100, unique=True, verbose_name='Instance namespace')),
                ('app_data', app_data.fields.AppDataField(default='{}', editable=False)),
                ('permalink_type', models.CharField(choices=[('s', 'the-eagle-has-landed/'), ('ys', '1969/the-eagle-has-landed/'), ('yms', '1969/07/the-eagle-has-landed/'), ('ymds', '1969/07/16/the-eagle-has-landed/'), ('ymdi', '1969/07/16/11/')], default='slug', help_text='Choose the style of urls to use from the examples. (Note, all types are relative to apphook)', max_length=8, verbose_name='permalink type')),
                ('non_permalink_handling', models.SmallIntegerField(choices=[(200, 'Allow'), (302, 'Redirect to permalink (default)'), (301, 'Permanent redirect to permalink'), (404, 'Return 404: Not Found')], default=302, help_text='How to handle non-permalink urls?', verbose_name='non-permalink handling')),
                ('paginate_by', models.PositiveIntegerField(default=5, help_text='When paginating list views, how many services per page?', verbose_name='Paginate size')),
                ('pagination_pages_start', models.PositiveIntegerField(default=10, help_text='When paginating list views, after how many pages should we start grouping the page numbers.', verbose_name='Pagination pages start')),
                ('pagination_pages_visible', models.PositiveIntegerField(default=4, help_text='When grouping page numbers, this determines how many pages are visible on each side of the active page.', verbose_name='Pagination pages visible')),
                ('exclude_featured', models.PositiveSmallIntegerField(blank=True, default=0, help_text='If you are using the Featured services plugin on the service list view, you may prefer to exclude featured services from the service list itself to avoid duplicates. To do this, enter the same number here as in your Featured services plugin.', verbose_name='Excluded featured services count')),
                ('template_prefix', models.CharField(blank=True, max_length=20, null=True, verbose_name='Prefix for template dirs')),
                ('search_indexed', models.BooleanField(default=True, help_text='Include services in search indexes?', verbose_name='Include in search index?')),
            ],
            options={
                'verbose_name': 'Section',
                'verbose_name_plural': 'Sections',
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ServicesConfigTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('app_title', models.CharField(max_length=234, verbose_name='name')),
                ('master', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='js_services.ServicesConfig')),
            ],
            options={
                'verbose_name': 'Section Translation',
                'db_table': 'js_services_servicesconfig_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
            },
        ),
        migrations.AddField(
            model_name='service',
            name='app_config',
            field=aldryn_apphooks_config.fields.AppHookConfigField(help_text='When selecting a value, the form is reloaded to get the updated default', on_delete=django.db.models.deletion.CASCADE, to='js_services.ServicesConfig', verbose_name='Section'),
        ),
        migrations.AlterUniqueTogether(
            name='servicesconfigtranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
