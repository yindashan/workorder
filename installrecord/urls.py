'''
Created on Jan 3, 2014

@author: aotian
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'installrecord.views.index',name="installrecord"),
    url(r'^index/$', 'installrecord.views.index', name="installrecord_index"),
    url(r'^search/$', 'installrecord.views.search', name="installrecord_search"),
    url(r'^add/$', 'installrecord.views.add',name="installrecord_add"),
    url(r'^edit/(?P<ir_id>\d+)/$', 'installrecord.views.edit',name="installrecord_edit"),
    url(r'^delete/(?P<ir_id>\d+)/$', 'installrecord.views.delete',name="installrecord_delete"),
)

