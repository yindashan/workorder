from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'software.views.index',name="software"),
    url(r'^index/$', 'software.views.index', name="software_index"),
    url(r'^customer_index/$', 'software.views.customer_index', name="software_customer_index"),
    url(r'^apply/(?P<sw_id>\d+)/$', 'software.views.apply_software', name="software_apply"),
    url(r'^add/$', 'software.views.add',name="software_add"),
    url(r'^edit/(?P<sw_id>\d+)/$', 'software.views.edit',name="software_edit"),
    #url(r'^delete/(?P<sw_id>\d+)/$', 'software.views.delete',name="software_delete"),
)