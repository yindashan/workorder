#!usr/bin/env python
#coding: utf-8
from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
     url(r'^$', 'dynamicconfig.views.search',name="dynamicconfig"),
     url(r'^search/$', 'dynamicconfig.views.search',name="dynamicconfig_search"),
)