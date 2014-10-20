#!/usr/bin/env python
# encoding: utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'ittask.views.index',name="ittask"),
    url(r'^index/$', 'ittask.views.index', name="ittask_index"),
    url(r'^search/$', 'ittask.views.search', name="ittask_search"),
    url(r'^add/$', 'ittask.views.add',name="ittask_add"),
    url(r'^watch/(?P<ittask_id>\d+)/$', 'ittask.views.watch',name="ittask_watch"),
    url(r'^close/(?P<ittask_id>\d+)/$', 'ittask.views.close',name="ittask_close"),
    url(r'^remark_add/(?P<ittask_id>\d+)/$', 'ittask.views.remark_add',name="ittask_remark_add"),
    url(r'^edit/(?P<ittask_id>\d+)/$', 'ittask.views.edit',name="ittask_edit"),
    url(r'^sedit/(?P<ittask_id>\d+)/$', 'ittask.views.sedit',name="ittask_sedit"),
    url(r'^mytask/$', 'ittask.views.mytask',name="ittask_mytask"),
    url(r'^myhistory/$', 'ittask.views.my_history',name="ittask_myhistory"),
    url(r'^mysearch/$', 'ittask.views.my_search',name="ittask_mysearch"),
)