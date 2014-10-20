#!usr/bin/env python
#coding: utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('',
     url(r'^$', 'staff.views.index',name="staff"),
     url(r'^index/$', 'staff.views.index', name="staff_index"),
     url(r'^add/$', 'staff.views.add', name="staff_add"),
     url(r'^edit/(?P<staff_id>\d+)/$', 'staff.views.edit',name="staff_edit"),
     url(r'^delete/(?P<staff_id>\d+)/$', 'staff.views.delete',name="staff_delete"),
     # 根据区域ID 查询对应区域的工程师信息
     url(r'^search/$', 'staff.views.search',name="staff_search"),
     url(r'^search_all/$', 'staff.views.search_all',name="staff_search_all"),
     # 同上，同时可以显示每个IT工程师的工作量
     url(r'^search_with_load/$', 'staff.views.search_with_load',name="staff_search_with_load"),
     # 获取推荐工程师的信息
     url(r'^recommend_engineer/$', 'staff.views.recommend_engineer',name="staff_recommend_engineer"),
)