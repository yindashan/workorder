#!usr/bin/env python
#coding: utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('',
     url(r'^add/$', 'order.views.add', name="order_add"),
     # 以下属于普通用户和话务员
     # 进行中的工单(普通用户&话务员)   状态: 2:已接受 4:已升级  3:已解决
     url(r'^in_hand/$', 'order.views.in_hand', name="order_in_hand"),
     # 历史工单(普通用户&话务员)   状态: 5:已评价
     url(r'^customer_history/$', 'order.views.customer_history', name="order_customer_history"),
     
     # 处理完成的工单(工程师)  状态:
     url(r'^engineer_complete/$', 'order.views.engineer_complete', name="order_engineer_complete"),

     # 待处理的工单　
     url(r'^pend/$', 'order.views.pend', name="order_pend"),
     # 处理工单
     url(r'^deal/(?P<order_id>\d+)/$', 'order.views.deal', name="order_deal"),
     # 查看工单(只读)
     url(r'^watch/(?P<order_id>\d+)/$', 'order.views.watch', name="order_watch"),
     # 提交备注
     url(r'^submit_comment/$', 'order.views.submit_comment', name="order_submit_comment"),
     # 待评价工单
     url(r'^appraise_index/$', 'order.views.appraise_index', name="order_appraise_index"),
     # 工单流转
     url(r'^wander/$', 'order.views.wander', name="order_wander"),
     # 对工单进行评价　
     url(r'^appraise/(?P<order_id>\d+)/$', 'order.views.appraise', name="order_appraise"),
     # 工单管理
     url(r'^index/$', 'order.views.index', name="order_index"),
     # 工单搜索
     url(r'^search/$', 'order.views.search', name="order_search"),
     
     # 工单评价的全路径
     url(r'^full_appraise/(?P<order_id>\d+)/$', 'order.views.full_appraise', name="order_full_appraise"),
    
     # 工单取消
     url(r'^cancel/$', 'order.views.cancel', name="order_cancel"),
#     # 临时需求--导出
#     url(r'^export/$', 'order.views.export', name="order_export"),
     
)