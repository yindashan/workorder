#!usr/bin/env python
# -*- coding:utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.models import User
#from django.contrib.auth.hashers import *
from django.contrib.auth import authenticate, login as auth_login ,logout as auth_logout
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required

# stdandard library
import datetime

# our own code
from authority.decorators import permission_required
from reports.models import pie_info

# 工单统计
@permission_required('order_stat')
def index(request):
    return render_to_response('report/index.html')
    
# 工单统计
@permission_required('order_stat')
def order_stat(request):
    # 时间区间前闭后开
    current_time = datetime.datetime.now()
    # 统计的开始时间
    start_time = request.POST.get('start_time', None)
    if start_time:
        print start_time,type(start_time)
        start_time += ' 00:00:00'
        start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    else:
        start_time = current_time - datetime.timedelta(7)
        
    # 统计的结束时间 
    end_time = request.POST.get('end_time', None)
    if end_time:
        end_time += ' 00:00:00'
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    else:
        end_time = current_time + datetime.timedelta(1)

    # 获取
    return render_to_response('report/order_stat.html',{'chart_list': pie_info(start_time, end_time)}) 
        
    
    
    
    
    
    
    
    
    