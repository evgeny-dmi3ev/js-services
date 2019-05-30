from django.conf.urls import url

from .views import (
    ServiceDetail, ServiceList, CategoryServiceList,
    YearServiceList, MonthServiceList, DayServiceList,
    ServiceSearchResultsList, ServiceFilteredList)
from .feeds import LatestServicesFeed, CategoryFeed

urlpatterns = [
    url(r'^$',
        ServiceList.as_view(), name='service-list'),
    url(r'^feed/$', LatestServicesFeed(), name='service-list-feed'),

    url(r'^search/$',
        ServiceSearchResultsList.as_view(), name='service-search'),

    url(r'^filtered/$',
        ServiceFilteredList.as_view(), name='service-filtered'),

    url(r'^(?P<year>\d{4})/$',
        YearServiceList.as_view(), name='service-list-by-year'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        MonthServiceList.as_view(), name='service-list-by-month'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$',
        DayServiceList.as_view(), name='service-list-by-day'),

    # Various permalink styles that we support
    # ----------------------------------------
    # This supports permalinks with <service_pk>
    # NOTE: We cannot support /year/month/pk, /year/pk, or /pk, since these
    # patterns collide with the list/archive views, which we'd prefer to
    # continue to support.
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<pk>\d+)/$',
        ServiceDetail.as_view(), name='service-detail'),
    # These support permalinks with <service_slug>
    url(r'^(?P<slug>\w[-\w]*)/$',
        ServiceDetail.as_view(), name='service-detail'),
    url(r'^(?P<year>\d{4})/(?P<slug>\w[-\w]*)/$',
        ServiceDetail.as_view(), name='service-detail'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<slug>\w[-\w]*)/$',
        ServiceDetail.as_view(), name='service-detail'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>\w[-\w]*)/$',  # flake8: NOQA
        ServiceDetail.as_view(), name='service-detail'),

    url(r'^category/(?P<category>\w[-\w]*)/$',
        CategoryServiceList.as_view(), name='service-list-by-category'),
    url(r'^category/(?P<category>\w[-\w]*)/feed/$',
        CategoryFeed(), name='service-list-by-category-feed'),
]
