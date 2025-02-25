# Generated by Django 2.2.28 on 2024-04-18 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('js_services', '0023_auto_20240123_0000'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicesconfig',
            name='show_in_search_filters',
            field=models.BooleanField(default=True, verbose_name='Show section in search filters'),
        ),
        migrations.AddField(
            model_name='servicesconfig',
            name='show_services_in_search_filters',
            field=models.BooleanField(default=True, verbose_name='Show services in search filters'),
        ),
    ]
