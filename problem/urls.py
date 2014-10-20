# -*- coding:utf-8 -*-

from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
     url(r'^$', 'problem.views.index',name="problem"),
     url(r'^index/$', 'problem.views.index', name="problem_index"),
     # 展示树
     url(r'^tree/$', 'problem.views.tree', name="problem_tree"),
     # 操作树
     url(r'^manipulate_tree/$', 'problem.views.manipulate_tree', name="problem_manipulate_tree"),
     # 用父节点ID查询子节点
     url(r'^search/$', 'problem.views.search', name="problem_search"),
     
)