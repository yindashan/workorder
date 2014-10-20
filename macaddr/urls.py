#!usr/bin/env python
#coding: utf-8
'''
Created on 2013-9-26

@author: jingwen.wu
'''

from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
  
     # Mac 地址搜索
     url(r'^mac_search/$', 'macaddr.views.mac_search', name="mac_search"),
     
)