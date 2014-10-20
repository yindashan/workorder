#!usr/bin/env python
# -*- coding:utf-8 -*-
#django
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect,HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import *
from django.contrib.auth import authenticate, login as auth_login ,logout as auth_logout
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required

#standard library
import json

#our own code
from dynamicconfig.models import search_user

# 首页  系统管理
@login_required
def search(request):
    if request.GET:
        #1. 处理参数
        keyword = request.GET.get('keyword')
        keyword = keyword.encode('utf-8')
        # 查询词过短
        user_list = []
        if len(keyword) < 3:
            return HttpResponse(json.dumps(user_list))
        
        
        if request.GET.get('exactSearch'):
            user_list = search_user(keyword, True)
        else:
            user_list = search_user(keyword, False)
        
        return HttpResponse(json.dumps(user_list))
    else:
        return  HttpResponseBadRequest(u"错误请求")
        
        
    