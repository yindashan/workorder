#!/usr/bin/env python
# encoding: utf-8
'''
Created on 2013-10-21

@author: jingwen.wu
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('',
     url(r'^$', 'feedback.views.index', name="feedback"),
     url(r'^index/$', 'feedback.views.index', name="feedback_index"),
     url(r'^add/$', 'feedback.views.add', name="feedback_add"),
     url(r'^edit/(?P<feedback_id>\d+)/$', 'feedback.views.edit', name="feedback_edit"),
     url(r'^close/(?P<feedback_id>\d+)/$', 'feedback.views.close', name="feedback_close"),
     url(r'^reply/(?P<feedback_id>\d+)/$', 'feedback.views.reply', name="feedback_reply"),
     url(r'^detail/(?P<feedback_id>\d+)/$', 'feedback.views.detail', name="feedback_detail"),
     url(r'^reply_top/(?P<reply_id>\d+)/$', 'feedback.views.reply_top', name="reply_top"),

)
