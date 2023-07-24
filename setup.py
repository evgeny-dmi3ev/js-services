# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from js_services import __version__

REQUIREMENTS = [
    'Django>=1.8',
    'aldryn-boilerplates',
    'aldryn-common>=0.1.3',
    'aldryn-translation-tools>=0.1.0',
    'django-cms>=3.2',
    'django-parler>=1.4',
    'django-filer>=0.9.9',
    'djangocms-text-ckeditor',
    'easy-thumbnails',
    'six',
    'django-filter',
    'django-crispy-forms',
]

setup(
    name='js-services',
    version=__version__,
    description=open('README.rst').read(),
    author='Compound Partners Ltd',
    author_email='hello@compoundpartners.co.uk',
    packages=find_packages(),
    platforms=['OS Independent'],
    install_requires=REQUIREMENTS,
    include_package_data=True,
    zip_safe=False,
)
