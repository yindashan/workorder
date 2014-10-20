#!usr/bin/env python
#coding: utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('',
     url(r'^$', 'executive.views.index',name="executive"),
     url(r'^index/$', 'executive.views.index', name="executive_index"),
     url(r'^add/$', 'executive.views.add', name="executive_add"),
     url(r'^edit/(?P<executive_id>\d+)/$', 'executive.views.edit',name="executive_edit"),
     url(r'^delete/(?P<executive_id>\d+)/$', 'executive.views.delete',name="executive_delete"),
)