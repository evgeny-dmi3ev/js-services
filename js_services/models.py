# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from aldryn_apphooks_config.fields import AppHookConfigField
from aldryn_categories.models import Category
from aldryn_categories.fields import CategoryManyToManyField
from aldryn_translation_tools.models import TranslatedAutoSlugifyMixin, TranslationHelperMixin
from cms.models.fields import PlaceholderField
from cms.models.pluginmodel import CMSPlugin
from cms.utils.i18n import get_current_language, get_redirect_on_fallback
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db import connection, models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import override, ugettext
from djangocms_text_ckeditor.fields import HTMLField
from sortedm2m.fields import SortedManyToManyField
from filer.fields.image import FilerImageField
from djangocms_icon.fields import Icon
from parler.models import TranslatableModel, TranslatedFields
from aldryn_newsblog.utils import get_plugin_index_data, get_request, strip_tags
from aldryn_newsblog.models import Article, NewsBlogConfig
from aldryn_people.models import Person


from .cms_appconfig import ServicesConfig
from .managers import RelatedManager

try:
    from django.utils.encoding import force_unicode
except ImportError:
    from django.utils.encoding import force_text as force_unicode


@python_2_unicode_compatible
class Service(TranslatedAutoSlugifyMixin,
              TranslationHelperMixin,
              TranslatableModel):

    # TranslatedAutoSlugifyMixin options
    slug_source_field_name = 'title'
    slug_default = _('untitled-service')
    # when True, updates the service's search_data field
    # whenever the service is saved or a plugin is saved
    # on the service's content placeholder.
    update_search_on_save = getattr(
        settings,
        'SERVICES_UPDATE_SEARCH_DATA_ON_SAVE',
        False
    )

    translations = TranslatedFields(
        title=models.CharField(_('title'), max_length=234),
        slug=models.SlugField(
            verbose_name=_('slug'),
            max_length=255,
            db_index=True,
            blank=True,
            help_text=_(
                'Used in the URL. If changed, the URL will change. '
                'Clear it to have it re-created automatically.'),
        ),
        lead_in=HTMLField(
            verbose_name=_('Summary'), default='',
            help_text=_(
                'The Summary gives the reader the main idea of the story, this '
                'is useful in overviews, lists or as an introduction to your '
                'service.'
            ),
            blank=True,
        ),
        meta_title=models.CharField(
            max_length=255, verbose_name=_('meta title'),
            blank=True, default=''),
        meta_description=models.TextField(
            verbose_name=_('meta description'), blank=True, default=''),
        meta_keywords=models.TextField(
            verbose_name=_('meta keywords'), blank=True, default=''),
        meta={'unique_together': (('language_code', 'slug', ), )},

        search_data=models.TextField(blank=True, editable=False)
    )

    content = PlaceholderField('service_content',
                               related_name='service_content')
    sidebar = PlaceholderField('service_sidebar',
                               related_name='service_sidebar')
    #app_config = AppHookConfigField(
        #ServicesConfig,
        #verbose_name=_('Section'),
        #help_text='',
    #)
    sections = models.ManyToManyField(
        ServicesConfig,
        verbose_name=_('Sections'),
        related_name='services',
    )
    categories = CategoryManyToManyField(Category,
                                         verbose_name=_('categories'),
                                         blank=True)
    publishing_date = models.DateTimeField(_('publishing date'),
                                           default=now)
    is_published = models.BooleanField(_('is published'), default=False,
                                       db_index=True)
    is_featured = models.BooleanField(_('is featured'), default=False,
                                      db_index=True)
    featured_image = FilerImageField(
        verbose_name=_('featured image'),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    # Setting "symmetrical" to False since it's a bit unexpected that if you
    # set "B relates to A" you immediately have also "A relates to B". It have
    # to be forced to False because by default it's True if rel.to is "self":
    #
    # https://github.com/django/django/blob/1.8.4/django/db/models/fields/related.py#L2144
    #
    # which in the end causes to add reversed releted-to entry as well:
    #
    # https://github.com/django/django/blob/1.8.4/django/db/models/fields/related.py#L977
    related = SortedManyToManyField('self', verbose_name=_('related services'),
                                    blank=True, symmetrical=True)

    companies = SortedManyToManyField('js_companies.Company',
         verbose_name=_('companies'), blank=True)

    objects = RelatedManager()

    class Meta:
        ordering = ['-publishing_date']

    def get_class(self):
        '''Return class name'''
        return self.__class__.__name__

    @property
    def app_config(self):
        try:
            reverse('{0}:service-list'.format(ServicesConfig.default_namespace))
            return ServicesConfig.objects.get(namespace=ServicesConfig.default_namespace)
        except:
            return self.sections.all()[0]

    @property
    def type(self):
        '''Service Type / Section.'''
        return self.app_config

    @property
    def type_slug(self):
        '''Service Type / Section Machine Name'''
        return self.app_config.namespace

    @property
    def published(self):
        """
        Returns True only if the service (is_published == True) AND has a
        published_date that has passed.
        """
        return (self.is_published and self.publishing_date <= now())

    @property
    def future(self):
        """
        Returns True if the service is published but is scheduled for a
        future date/time.
        """
        return (self.is_published and self.publishing_date > now())

    def get_absolute_url(self, language=None):
        """Returns the url for this Service in the selected permalink format."""
        if not language:
            language = get_current_language()
        kwargs = {}
        permalink_type = self.app_config.permalink_type
        if 'y' in permalink_type:
            kwargs.update(year=self.publishing_date.year)
        if 'm' in permalink_type:
            kwargs.update(month="%02d" % self.publishing_date.month)
        if 'd' in permalink_type:
            kwargs.update(day="%02d" % self.publishing_date.day)
        if 'i' in permalink_type:
            kwargs.update(pk=self.pk)
        if 's' in permalink_type:
            slug, lang = self.known_translation_getter(
                'slug', default=None, language_code=language)
            if slug and lang:
                site_id = getattr(settings, 'SITE_ID', None)
                if get_redirect_on_fallback(language, site_id):
                    language = lang
                kwargs.update(slug=slug)

        if self.app_config and self.app_config.namespace:
            namespace = '{0}:'.format(self.app_config.namespace)
        else:
            namespace = ''

        with override(language):
            return reverse('{0}service-detail'.format(namespace), kwargs=kwargs)

    def get_search_data(self, language=None, request=None):
        """
        Provides an index for use with Haystack, or, for populating
        Service.translations.search_data.
        """
        if not self.pk:
            return ''
        if language is None:
            language = get_current_language()
        if request is None:
            request = get_request(language=language)
        description = self.safe_translation_getter('lead_in', '')
        text_bits = [strip_tags(description)]
        for category in self.categories.all():
            text_bits.append(
                force_unicode(category.safe_translation_getter('name')))
        for tag in self.tags.all():
            text_bits.append(force_unicode(tag.name))
        if self.content:
            plugins = self.content.cmsplugin_set.filter(language=language)
            for base_plugin in plugins:
                plugin_text_content = ' '.join(
                    get_plugin_index_data(base_plugin, request))
                text_bits.append(plugin_text_content)
        return ' '.join(text_bits)

    def save(self, *args, **kwargs):
        # Update the search index
        if self.update_search_on_save:
            self.search_data = self.get_search_data()

        # slug would be generated by TranslatedAutoSlugifyMixin
        super(Service, self).save(*args, **kwargs)

    def __str__(self):
        return self.safe_translation_getter('title', any_language=True) if self.pk else ''

    def services_by_category(self, category=None):
        if category:
            categories = Category.objects.filter(translations__slug=category)
            return Service.objects.published().filter(categories__in=categories[0].get_descendants()).distinct().exclude(pk=self.pk) if categories.count() else []
        return Service.objects.published().exclude(pk=self.pk)

    def related_categories(self, category=None):
        if category:
            categories = Category.objects.filter(translations__slug=category)
            return categories[0].get_descendants().filter(pk__in=self.categories.all()) if categories.count() else []
        return self.categories.all()

    def related_articles(self, article_category=None):
        if article_category:
            return Article.objects.published().filter(services=self, app_config__namespace=article_category)
        return Article.objects.published().filter(services=self)

    def services(self, service_category=None):
        if service_category:
            return Service.objects.published().filter(sections__namespace=service_category)
        return Service.objects.published()

    def people(self):
        return Person.objects.published().filter(services=self)

    def related_people(self):
        return Person.objects.published().filter(services__in=self.related.all()).distinct()


    def __getattr__(cls, name):
        if not hasattr(Service, name):
            if name.startswith('related_articles_'):
                category = name.split('related_articles_')[1].replace('_', '-')
                def wrapper(self):
                    return self.related_articles(category)
                setattr(Service, name, wrapper)
                return getattr(cls, name)
            elif name.startswith('services_by_category_'):
                category = name.split('services_by_category_')[1].replace('_', '-')
                def wrapper(self):
                    return self.services_by_category(category)
                setattr(Service, name, wrapper)
                return getattr(cls, name)
            elif name.startswith('related_categories_'):
                category = name.split('related_categories_')[1].replace('_', '-')
                def wrapper(self):
                    return self.related_categories(category)
                setattr(Service, name, wrapper)
                return getattr(cls, name)
            elif name.startswith('services_'):
                category = name.split('services_')[1].replace('_', '-')
                def wrapper(self):
                    return self.services(category)
                setattr(Service, name, wrapper)
                return getattr(cls, name)
        raise AttributeError


@python_2_unicode_compatible
class RelatedServicesPlugin(CMSPlugin):

    # NOTE: This one does NOT subclass NewsBlogCMSPlugin. This is because this
    # plugin can really only be placed on the article detail view in an apphook.
    cmsplugin_ptr = models.OneToOneField(
        CMSPlugin, related_name='+', parent_link=True)

    title = models.CharField(max_length=255, blank=True, verbose_name=_('Title'))
    icon = Icon(blank=False, default='fa-')
    image = FilerImageField(null=True, blank=True, related_name='+')
    count = models.PositiveSmallIntegerField(verbose_name=_('Number services'))
    layout = models.CharField(max_length=30, verbose_name=_('layout'))
    related_services = SortedManyToManyField('js_services.Service', verbose_name=_('related services'), blank=True, symmetrical=False)
    related_sections = SortedManyToManyField(ServicesConfig, verbose_name=_('related sections'), blank=True, symmetrical=False)
    related_people = SortedManyToManyField(Person, verbose_name=_('key people'), blank=True, symmetrical=False)
    related_companies = SortedManyToManyField('js_companies.Company', verbose_name=_('related companies'), blank=True, symmetrical=False)
    related_categories = SortedManyToManyField('aldryn_categories.Category', verbose_name=_('related categories'), blank=True, symmetrical=False)

    def copy_relations(self, oldinstance):
        self.related_services = oldinstance.related_services.all()
        self.related_sections = oldinstance.related_sections.all()
        self.related_people = oldinstance.related_people.all()
        self.related_companies = oldinstance.related_companies.all()
        self.related_categories = oldinstance.related_categories.all()

    def __str__(self):
        return str(self.pk)


@receiver(post_save, dispatch_uid='service_update_search_data')
def update_search_data(sender, instance, **kwargs):
    """
    Upon detecting changes in a plugin used in an service's content
    (PlaceholderField), update the service's search_index so that we can
    perform simple searches even without Haystack, etc.
    """
    is_cms_plugin = issubclass(instance.__class__, CMSPlugin)

    if Service.update_search_on_save and is_cms_plugin:
        placeholder = (getattr(instance, '_placeholder_cache', None) or
                       instance.placeholder)
        if hasattr(placeholder, '_attached_model_cache'):
            if placeholder._attached_model_cache == Service:
                service = placeholder._attached_model_cache.objects.language(
                    instance.language).get(content=placeholder.pk)
                service.search_data = service.get_search_data(instance.language)
                service.save()
