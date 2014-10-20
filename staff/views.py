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
import json
import time

# our own code
from staff.models import Staff
from utils.constants import yes_no_dict, weight_dict
from order.models import designate_engineer
from area.models import Area
from order.models import Order
from order.models import executive_helper
from authority.decorators import permission_required


##显示应用列表
@permission_required('config_manage')
def index(request):
    item_list = Staff.objects.filter(is_deleted=0).order_by("area","accountname")
    
    paginator = Paginator(item_list, 10)
    currentPage = request.POST.get('pageNum',1)
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)
    
    return render_to_response('staff/index.html',{'staff_list':pager, 'yes_no_dict':yes_no_dict})
    
    
@permission_required('config_manage')  
def add(request):
    if request.POST:
        area_id = int(request.POST.get('area_id'))
        realname = request.POST.get('realname')
        accountname = request.POST.get('accountname')
        is_available_list = request.POST.getlist('is_available')
        phone = request.POST.get('phone')
        weight = int(request.POST.get('weight'))
        email = request.POST.get('email')
        
        # 不允许重复添加
        staff_list = Staff.objects.filter(accountname=accountname, is_deleted=0)
        if staff_list:
            return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'此IT员工已存在,不允许重复添加!'}), mimetype='application/json')
            
        staff = Staff()
        # 一类特殊情况，IT工程师删除以后又被重新加入
        staff_list = Staff.objects.filter(accountname=accountname, is_deleted=1)
        if staff_list:
            staff = staff_list[0]
        
        staff.area_id = area_id
        staff.realname = realname
        staff.accountname = accountname
        staff.phone = phone
        staff.weight = weight
        staff.is_deleted = 0
        staff.email = email
        
        if is_available_list:
            staff.is_available = 1
        else:
            staff.is_available = 0
            
        staff.save()
        
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/staff/index", "message":u'添加成功'}), mimetype='application/json')
    else:
        # 区域
        area_list = Area.objects.all()
        return render_to_response('staff/add.html',{'area_list':area_list,'weight_dict':weight_dict}) 
    
@permission_required('config_manage') 
def edit(request, staff_id):
    staff = None
    try:
        staff = Staff.objects.get(id=int(staff_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'员工不存在!'}), mimetype='application/json')
    if request.POST:
        area_id = int(request.POST.get('area_id'))
        is_available_list = request.POST.getlist('is_available')
        phone = request.POST.get('phone')
        weight = int(request.POST.get('weight'))
        
        staff.area_id = area_id
        if is_available_list:
            staff.is_available = 1
        else:
            staff.is_available = 0
        staff.phone = phone  
        staff.weight = weight
        staff.save()
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/staff/index", "message":u'编辑成功'}), mimetype='application/json')
    else:
        # 区域
        area_list = Area.objects.all()
        return render_to_response('staff/edit.html',{'area_list':area_list, 'staff':staff,'weight_dict':weight_dict}) 
        
    
@permission_required('config_manage')   
def delete(request, staff_id):
    staff = None
    try:
        staff = Staff.objects.get(id=int(staff_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'员工不存在!'}), mimetype='application/json')
    
    staff.is_available = 0;
    staff.is_deleted = 1;
    staff.save()
    return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/staff/index", "message":u'删除成功'}), mimetype='application/json')

@login_required
def search(request):
    if request.method=='GET':
        area_id = int(request.GET.get('area_id'))
        staff_list = Staff.objects.filter(area_id=area_id, is_available=1)
        res_list = []
        for staff in staff_list:
            item = {}
            item['id'] = staff.id
            item['realname'] = staff.realname
            res_list.append(item)
            
        return HttpResponse(json.dumps(res_list))
    else:
        return  HttpResponseBadRequest(u"错误请求")
        
@login_required
def search_all(request):
    if request.method=='GET':
        area_id = int(request.GET.get('area_id'))
        staff_list = Staff.objects.filter(area_id=area_id, is_deleted=0)
        res_list = []
        for staff in staff_list:
            item = {}
            item['id'] = staff.id
            item['realname'] = staff.realname
            res_list.append(item)
            
        return HttpResponse(json.dumps(res_list))
    else:
        return  HttpResponseBadRequest(u"错误请求")
        
# 带工作量
@login_required
def search_with_load(request):
    if request.method=='GET':
        area_id = int(request.GET.get('area_id'))
        staff_list = Staff.objects.filter(area_id=area_id, is_available=1)
        res_list = []
        for staff in staff_list:
            item = {}
            item['id'] = staff.id
            # 此员工当天接受的工单数
            start_time = time.strftime('%Y-%m-%d',time.localtime())
            count = Order.objects.filter(area_id=area_id,create_time__gte=start_time, 
                    dealer_accountname=staff.accountname).count()
            item['realname'] = staff.realname + '(' + str(count) + ')'
            res_list.append(item)
            
        return HttpResponse(json.dumps(res_list))
    else:
        return  HttpResponseBadRequest(u"错误请求")
        
# 供前端ajax调用,推荐工程师
@login_required
def recommend_engineer(request):
    if request.method=='GET':
        area_id = int(request.GET.get('area_id',1))
        accountname = request.GET.get('accountname')
        
        order = Order()
        order.creator = request.user.username
        order.accountname = accountname
        
        dd = {}
        
        staff = executive_helper(order)
        
        if staff:
            # 优先级 1:'紧急',2:'普通'
            dd['priority_level'] = 1
        else:
            staff = designate_engineer(area_id)
            dd['priority_level'] = 2
        
        comment = ''
        if staff:
            comment = u"系统推荐:" + staff.area.name + ' ' + staff.realname
            dd['comment'] = comment
            dd['id'] = staff.id
            dd['area_id'] = staff.area.id
        else:
            comment = u"此区域没有对应的IT工程师"
            dd['comment'] = comment
            
        return HttpResponse(json.dumps(dd))
    else:
        return  HttpResponseBadRequest(u"错误请求")
    





    
