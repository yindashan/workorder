#!usr/bin/env python
#coding: utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'area.views.index',name="area"),
    url(r'^index/$', 'area.views.index', name="area_index"),
    url(r'^add/$', 'area.views.add',name="area_add"),
    url(r'^edit/(?P<area_id>\d+)/$', 'area.views.edit',name="area_edit"),
)