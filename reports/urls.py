# -*- coding:utf-8 -*-

from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    url(r'^$', 'reports.views.index',name="report_index"),
    url(r'^index/$', 'reports.views.index',name="report_index"),
    url(r'^order_stat/$', 'reports.views.order_stat', name="order_stat"),

)