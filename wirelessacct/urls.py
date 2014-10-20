# -*- coding:utf-8 -*-

from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    url(r'^$', 'wirelessacct.views.index',name="wirelessacct_index"),
    url(r'^index/$', 'wirelessacct.views.index',name="wirelessacct_index"),
    url(r'^add/$', 'wirelessacct.views.add',name="wirelessacct_add"),
    url(r'^stop/(?P<record_id>\d+)/$', 'wirelessacct.views.stop',name="wirelessacct_stop"),
    url(r'^detail/(?P<record_id>\d+)/$', 'wirelessacct.views.detail',name="wirelessacct_detail"),
    url(r'^history/$', 'wirelessacct.views.history',name="wirelessacct_history"),
)