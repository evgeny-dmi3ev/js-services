# Generated by Django 2.2.10 on 2020-07-17 10:02

from django.db import migrations, models
import js_color_picker.fields


class Migration(migrations.Migration):

    dependencies = [
        ('js_services', '0018_auto_20200625_2353'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicetranslation',
            name='is_featured_trans',
            field=models.BooleanField(db_index=True, default=False, verbose_name='is featured'),
        ),
        migrations.AddField(
            model_name='servicetranslation',
            name='is_published_trans',
            field=models.BooleanField(db_index=True, default=False, verbose_name='is published'),
        ),
        migrations.AlterField(
            model_name='relatedservicesplugin',
            name='background_color',
            field=js_color_picker.fields.RGBColorField(blank=True, colors={'#0073CF': 'Blue 2', '#00B0CA': 'Blue 1', '#00ae65': 'green', '#0D2240': 'dark-blue', '#4d4d4d': 'grey', '#5E6A71': 'dark-grey', '#67B2E8': 'pale-blue', '#808080': 'middle-grey', '#C3009E': 'Purple', '#CAD7E6': 'Light 2', '#D1EAEC': 'Light 1', '#E00034': 'Dark red', '#E1F0FA': 'palest-blue', '#E8CFDC': 'Light purple', '#F0AB00': 'Dark yellow', '#F7D1C2': 'Light red', '#FEEDCA': 'Light yellow', '#ccc': 'light-grey', '#eee': 'lightest-grey'}, mode='choice', null=True, verbose_name='Background Color'),
        ),
    ]