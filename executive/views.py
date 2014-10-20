#!usr/bin/env python
# -*- coding:utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
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


# stdandard library
from executive.models import Executive, ExecutiveExtend
from area.models import Area
from authority.decorators import permission_required


##显示应用列表
@permission_required('config_manage')
def index(request):
    item_list = Executive.objects.order_by("accountname")
    
    paginator = Paginator(item_list, 10)
    currentPage = request.POST.get('pageNum',1)
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)
    
    pager.object_list = change(pager.object_list)
    return render_to_response('executive/index.html',{'executive_list':pager})
    
def change(executive_list):
    res_list = []
    for item in executive_list:
        res_list.append(ExecutiveExtend(item))
    return res_list
        
    
@permission_required('config_manage')  
def add(request):
    if request.POST:
        realname = request.POST.get('realname')
        accountname = request.POST.get('accountname')
        department = request.POST.get('department')
        email = request.POST.get('email')
        job = request.POST.get('job')
        first_engineer_id = request.POST.get('first_engineer_id')
        second_engineer_id = request.POST.get('second_engineer_id')
        
        executive = Executive()
        executive.realname = realname
        executive.accountname = accountname
        executive.email = email
        executive.department = department
        executive.job = job
        executive.first_engineer_id = first_engineer_id
        executive.second_engineer_id = second_engineer_id
        executive.save()
        
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/executive/index", "message":u'添加成功'}), mimetype='application/json')
    else:
        area_list = Area.objects.all()
        return render_to_response('executive/add.html',{'area_list':area_list}) 
    
@permission_required('config_manage')
def edit(request, executive_id):
    executive = None
    try:
        obj = Executive.objects.get(id=int(executive_id))
        executive = ExecutiveExtend(obj)
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'高管不存在!'}), mimetype='application/json')
    
    if request.POST:
        department = request.POST.get('department')
        job = request.POST.get('job')
        first_engineer_id = request.POST.get('first_engineer_id')
        second_engineer_id = request.POST.get('second_engineer_id')
        
        obj.department = department
        obj.job = job
        obj.first_engineer_id = first_engineer_id
        obj.second_engineer_id = second_engineer_id
        obj.save()
        
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/executive/index", "message":u'编辑成功'}), mimetype='application/json')
    else:
        area_list = Area.objects.all()
        return render_to_response('executive/edit.html', {'area_list':area_list, 'executive':executive})  
       
  
@permission_required('config_manage')
def delete(request, executive_id):
    executive = None
    try:
        executive = Executive.objects.get(id=int(executive_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'高管不存在!'}), mimetype='application/json')
    
    executive.delete()
    return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/executive/index", "message":u'删除成功'}), mimetype='application/json')
    




    
