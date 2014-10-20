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
#import json
import datetime

# our own code
from order.models import Order,Remark,OrderExtend,Wander,genCaseID,designate_engineer,executive_helper
from utils.constants import priority_dict, wander_action_dict, order_status_dict
from problem.models import ProblemType,getProblemType
from staff.models import Staff
from area.models import Area
from authority.models import get_managable_area, get_managable_area_id
from notify.models import distribute_customer, distribute_engineer, sms_notify, cancel_customer
from notify.models import retransmission_customer,wait_appraise_customer,retransmission_engineer
from account.models import getUser
from dynamicconfig.models import search_user
from authority.decorators import permission_required

@login_required    
def add(request):
    # 一级问题类目
    first_level_problem_list = ProblemType.objects.filter(level=1, is_available=1)
    # 区域
    area_list = Area.objects.all()
    
    if request.POST:
        # 1) 保存工单记录
        order = Order()
        # 创建时间
        order.create_time = datetime.datetime.now()
        # creator
        order.creator = request.user.username
        # 故障申报人姓名
        order.realname = request.POST.get('realname')
        # 账户名（故障申报人) 
        order.accountname = request.POST.get('accountname')
        # 部门
        order.department = request.POST.get('department')
        # 电子邮件
        order.email = request.POST.get('email')
        # 电话
        order.phone = request.POST.get('phone')
        # 所属区域
        order.area_id = int(request.POST.get('area_id'))
        # 故障类目(三级)
        order.problem_type_third = int(request.POST.get('third_level_problem'))
        # 故障描述
        order.problem_desc = request.POST.get('problem_desc')
        # 优先级 1:优先 2:普通
        order.priority_level = int(request.POST.get('priority_level',2))
        # 状态 1.已接受
        order.status = 2
        # 工单编号 
        order.case_number = genCaseID()
        # 工位
        order.workseat = request.POST.get('workseat')
        
        # IT工程师ID
        deal_engineer_id = request.POST.get('deal_engineer_id',None)
        
        # 来源
        # 话务员
        if 'order_feedback' in request.session["authority_set"]:
            order.source = 1   # 电话
        else:
            order.source = 2   # 网络　
            
        # 校验下申报人是否合法
        res_list = search_user(order.accountname, True)
        #print res_list
        if res_list == None or len(res_list) > 1:
            return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'申报人不是合法用户!'}), mimetype='application/json')
        
        # 人工指派
        if deal_engineer_id:
            staff = Staff.objects.get(id=deal_engineer_id)
            
        # 系统指派 又分为两种 1) 高管　2) 非高管
        else:
            staff = executive_helper(order)
            if staff:
                # 1:'优先',2:'普通'
                order.priority_level = 1
            else:
                staff = designate_engineer(order.area_id)
            
        # 处理人的账户名称
        order.dealer_accountname = staff.accountname
        # 处理人的用户名
        order.dealer_realname = staff.realname
        
        # 工单处理结果的默认评级
        order.feedback_rate = 5
        
        order.save()
        
        # 2) 流转记录
        wander = Wander()
        wander.create_time = datetime.datetime.now()
        wander.source_name = order.realname
        wander.target_name = order.dealer_realname
        wander.operation = 1
        wander.order = order
        wander.save()
        
        # 3) 短信邮件通知
        # 邮件发送给申报人
        distribute_customer.delay(order)
        
        # 邮件发送给工程师
        distribute_engineer.delay(order)
        
        # 短信发送给工程师
        sms_notify.delay(order)
        
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/order/in_hand", "message":u'工单提交成功'}), mimetype='application/json')
    return render_to_response('order/add.html',{'area_list':area_list, 'priority_dict':priority_dict, 
        'user':request.user,'first_level_problem_list':first_level_problem_list,'auth_set':request.session["authority_set"]}) 

# 工单处理中
@login_required 
def in_hand(request):
    item_list = Order.objects.filter(creator=request.user.username,status__in=[2,3,4]).order_by('status','-create_time')
    paginator = Paginator(item_list, 10)
    currentPage = request.POST.get('pageNum',1)
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)
        
    pager.object_list = change(pager.object_list, request)
    return render_to_response('order/in_hand.html',{'order_list':pager})
    
def change(item_list, request):
    res_list = []
    for item in item_list:
        res_list.append(OrderExtend(item,request))
    return res_list

# 我的工单 
@login_required
def customer_history(request):
    # 一级问题类目
    first_level_problem_list = ProblemType.objects.filter(level=1, is_available=1)
    # 区域
    area_list = Area.objects.all()
    return render_to_response('order/customer_history.html',{'area_list':area_list, 'order_status_dict':order_status_dict,
            'priority_dict':priority_dict, 'first_level_problem_list':first_level_problem_list,'user':request.user })

    
# 查看工单
@login_required
def watch(request, order_id):
    # 工单
    order = Order.objects.get(id=order_id)
    # 备注
    remark_list = Remark.objects.filter(order_id=order_id)
    # 流转记录
    wander_list = Wander.objects.filter(order_id=order_id)
    # 问题类目
    problem_type = getProblemType(order.problem_type_third)
    
    return render_to_response('order/watch.html',{'order':order,'remark_list':remark_list, 
        'wander_list':wander_list,'wander_action_dict':wander_action_dict, 
        'priority_dict':priority_dict,'problem_type':problem_type, 'user':request.user})
    

# 以下属于IT工程师
# 待处理的工单  deal_order
@permission_required('deal_order')
def pend(request):
    item_list = Order.objects.filter(dealer_accountname=request.user.username,status__in=[2,4]).order_by('priority_level', '-create_time')
    
    paginator = Paginator(item_list, 10)
    currentPage = request.POST.get('pageNum',1)
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)
        
    pager.object_list = change(pager.object_list, request)
    return render_to_response('order/pend.html',{'order_list':pager})
    
# 处理工单
@permission_required('deal_order')
def deal(request, order_id):
    if request.method =='POST':
        # 1) 备注
        remark = Remark()
        remark.create_time = datetime.datetime.now()
        remark.accountname = request.user.username
        remark.realname = request.user.userprofile.realname
        remark.order_id = order_id
        remark.comment = request.POST.get('comment')
        remark.save()
        
        # 2) 修改工单状态
        order = Order.objects.get(id=order_id)
        # 1.未接受 2. 已接受  3.已解决(已关闭) 4. 已升级 5. 已评价 6. 已取消
        order.status = 3
        order.close_time = datetime.datetime.now()
        order.save()
        
        # 3) 流转记录
        wander = Wander()
        wander.create_time = datetime.datetime.now()
        wander.source_name = order.dealer_realname
        wander.target_name = order.realname
        wander.operation = 3
        wander.order = order
        wander.save()
        
        # 4) 短信邮件通知
        # 发送给申报人
        wait_appraise_customer.delay(order)
        
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/order/pend", "message":u'工单状态修改成功.'}), mimetype='application/json')
    else:
        # 工单
        order = Order.objects.get(id=order_id)
        #print order.dealer_accountname
        # 备注
        remark_list = Remark.objects.filter(order_id=order_id)
        # 流转记录
        wander_list = Wander.objects.filter(order_id=order_id)
        # 问题类目
        problem_type = getProblemType(order.problem_type_third)
        # 区域
        area_list = Area.objects.all()
        #print request.session["authority_set"]
        
        return render_to_response('order/deal.html',{'order':order,'remark_list':remark_list, 
            'wander_list':wander_list,'wander_action_dict':wander_action_dict, 'area_list':area_list,
            'priority_dict':priority_dict,'problem_type':problem_type,'user':request.user,
            'auth_set':request.session["authority_set"]})

# 提交备注
@login_required
def submit_comment(request):
    if request.POST:
        # 保存备注
        remark = Remark()
        remark.create_time = datetime.datetime.now()
        remark.accountname = request.user.username
        remark.realname = request.user.userprofile.realname
        remark.order_id = int(request.POST.get('order_id'))
        remark.comment = request.POST.get('comment')
        remark.save()
        
        return HttpResponse()
    else:
        return  HttpResponseBadRequest(u"错误请求")

# 工单流转
@login_required  
def wander(request):
    if request.POST:
        # 保存备注
        order_id = int(request.POST.get('order_id'))
        staff_id = int(request.POST.get('staff_id'))
        comment = request.POST.get('comment')
        
        staff = Staff.objects.get(id=staff_id)
        order = Order.objects.get(id=order_id)
        
        # 1) 流转记录
        wander = Wander()
        wander.create_time = datetime.datetime.now()
        wander.source_name = order.dealer_realname
        wander.target_name = staff.realname
        wander.operation = 2
        wander.order = order
        wander.save()
        
        # 2) 备注信息
        if comment:
            remark = Remark()
            remark.create_time = datetime.datetime.now()
            remark.accountname = request.user.username
            remark.realname = request.user.userprofile.realname
            remark.order_id = order_id
            remark.comment = comment
            remark.save()
        
        # 3) 修改公告单处理人
        order.dealer_realname = staff.realname
        order.dealer_accountname = staff.accountname
        # 1.未接受 2. 已接受  3.已解决(已关闭) 4. 已升级 5. 已评价 6. 已取消
        order.status = 4
        order.save()
        
        # 4) 邮件短信通知
        # 邮件发送给申报人
        retransmission_customer.delay(order)
        
        # 邮件发送给工程师
        retransmission_engineer.delay(order)
        
        # 短信发送给工程师
        sms_notify.delay(order)
        
        return HttpResponse(simplejson.dumps({"statusCode":200, 
            "message":u'工单升级成功.'}), mimetype='application/json')
    else:
        return  HttpResponseBadRequest(u"错误请求")

#  待评价的工单
@permission_required('order_feedback')
def appraise_index(request):
    item_list = Order.objects.filter(status=3).order_by('priority_level', '-create_time')
    paginator = Paginator(item_list, 10)
    currentPage = request.POST.get('pageNum',1)
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)
        
    pager.object_list = change(pager.object_list, request)
    return render_to_response('order/appraise_index.html',{'order_list':pager})
    
# 评价
@login_required
def appraise(request, order_id):
    if request.method =='POST':
        # 1) 工单
        order = Order.objects.get(id=order_id)
        order.feedback_rate = int(request.POST.get('score'))
        order.feedback_comment = request.POST.get('feedback_comment')
        order.status = 5
        order.save()
        
        # 2) 流转记录
        wander = Wander()
        wander.create_time = datetime.datetime.now()
        wander.source_name = order.realname
        wander.target_name = u'系统'
        wander.operation = 4
        wander.order = order
        wander.save()
        
        url = '/order/in_hand'
        # 话务员
        if 'order_feedback' in request.session["authority_set"]:
            url = '/order/appraise_index'
            
        return HttpResponse(simplejson.dumps({"statusCode":200,"url":url, "message":u'工单评价成功.'}), mimetype='application/json')
        
    else:
        # 工单
        order = Order.objects.get(id=order_id)
        # 备注
        remark_list = Remark.objects.filter(order_id=order_id)
        # 流转记录
        wander_list = Wander.objects.filter(order_id=order_id)
        # 问题类目
        problem_type = getProblemType(order.problem_type_third)
        return render_to_response('order/appraise.html',{'order':order,
            'remark_list':remark_list,'wander_list':wander_list,'wander_action_dict':wander_action_dict,
            'priority_dict':priority_dict,'problem_type':problem_type, 
            'user':request.user})
   
# 工单管理　
# 针对区域主管和IT主管
@permission_required('order_manage')
def index(request):
    # 一级问题类目
    first_level_problem_list = ProblemType.objects.filter(level=1, is_available=1)
    # 区域
    area_list = get_managable_area(request)
    return render_to_response('order/index.html',{'area_list':area_list,
            'order_status_dict':order_status_dict,'priority_dict':priority_dict,
            'first_level_problem_list':first_level_problem_list})

# 工单管理　
# 针对区域主管和IT主管
@permission_required('deal_order')
def engineer_complete(request):
    # 一级问题类目
    first_level_problem_list = ProblemType.objects.filter(level=1, is_available=1)
    # 区域
    area_list = Area.objects.all()
    return render_to_response('order/engineer_complete.html',{'area_list':area_list, 
            'order_status_dict':order_status_dict,'priority_dict':priority_dict, 
            'first_level_problem_list':first_level_problem_list,'user':request.user})
# 搜索        
@login_required
def search(request):
    if request.method == 'POST':
        # 工单编号
        case_number = request.POST.get('case_number')
        #　申报人
        realname = request.POST.get('realname')
        # 处理人
        dealer_realname = request.POST.get('dealer_realname')
        # 优先级
        priority_level = request.POST.get('priority_level')
        # 开始时间
        start_time = request.POST.get('start_time')
        # 结束时间
        end_time = request.POST.get('end_time')
        # 问题类别
        problem_type_third = request.POST.get('third_level_problem')
        # 状态
        status = request.POST.get('status')
        # 区域
        area_id = request.POST.get('area_id')
        # 提交人 
        creator = request.POST.get('submitor')
        
        # 是否需要检查区域的管理权限(工单管理中需要此功能)
        # 存在安全隐患
        need_area_check = request.POST.get('need_area_check',False)
        
        
        # FIXME 注意权限控制
        res_list = Order.objects.all().order_by('status','priority_level', '-create_time')
        
        if need_area_check:
            area_id_list = get_managable_area_id(request)
            res_list = res_list.filter(area_id__in=area_id_list)
        
        if case_number:
            res_list = res_list.filter(case_number=case_number)
        
        if realname:
            res_list = res_list.filter(realname__contains=realname)
        
        if dealer_realname:
            res_list = res_list.filter(dealer_realname__contains=dealer_realname)
            
        if priority_level:
            res_list = res_list.filter(priority_level=priority_level)
            
        if start_time:
            start_time = datetime.datetime.strptime(start_time,'%Y-%m-%d')
            res_list = res_list.filter(create_time__gte=start_time)
        
        if end_time:
            # 2013-04-14
            end_time = datetime.datetime.strptime(end_time,'%Y-%m-%d')
            end_time = end_time + datetime.timedelta(days= 1)
            
            res_list = res_list.filter(create_time__lt=end_time)
            
        if problem_type_third:
            res_list = res_list.filter(problem_type_third=problem_type_third)
            
        if status:
            res_list = res_list.filter(status=status)
        
        if area_id:
            res_list = res_list.filter(area_id=area_id)
            
        if creator:
            res_list = res_list.filter(creator=creator)
            
        paginator = Paginator(res_list, 10)
        currentPage = request.POST.get('pageNum', 1)
        try:
            pager = paginator.page(currentPage)
        except InvalidPage:
            pager = paginator.page(1)
        
        pager.object_list = change(pager.object_list, request)
        
        #print request.session["authority_set"]
        return render_to_response('order/searchback.html',{'order_list':pager,'auth_set':request.session["authority_set"]})
    else:
        return  HttpResponseBadRequest(u"错误请求")
        
@login_required        
def full_appraise(request, order_id):
    # 部分应用中监控项读权限
    auth_set = request.session["authority_set"]
    user = getUser(request.user.id)  
    # 工单
    order = Order.objects.get(id=order_id)
    # 备注
    remark_list = Remark.objects.filter(order_id=order_id)
    # 流转记录
    wander_list = Wander.objects.filter(order_id=order_id)
    # 问题类目
    problem_type = getProblemType(order.problem_type_third)
    
    return render_to_response('order/full_appraise.html',{'user':user,'auth_set':auth_set,'order':order,
            'remark_list':remark_list,'wander_list':wander_list,'wander_action_dict':wander_action_dict,
            'priority_dict':priority_dict,'problem_type':problem_type }) 

# 取消工单(拒绝不合理的工单)
@permission_required('order_cancel')    
def cancel(request):
    if request.POST:
        # 保存备注
        order_id = int(request.POST.get('order_id'))
        comment = request.POST.get('comment')
        
        order = Order.objects.get(id=order_id)
        
        # 1) 流转记录
        wander = Wander()
        wander.create_time = datetime.datetime.now()
        wander.source_name = order.dealer_realname
        wander.target_name = order.realname
        wander.operation = 5
        wander.order = order
        wander.save()
        
        # 2) 备注信息
        if comment:
            remark = Remark()
            remark.create_time = datetime.datetime.now()
            remark.accountname = request.user.username
            remark.realname = request.user.userprofile.realname
            remark.order_id = order_id
            remark.comment = comment
            remark.save()
        
        # 1.未接受 2. 已接受  3.已解决(已关闭) 4. 已升级 5. 已评价 6. 已取消
        order.status = 6
        order.close_time = datetime.datetime.now()
        order.save()
                
        # 3) 发送邮件
        cancel_customer.delay(order, request.user, comment)
        
        return HttpResponse(simplejson.dumps({"statusCode":200,
            "message":u'工单取消成功.'}), mimetype='application/json')
    else:
        return  HttpResponseBadRequest(u"错误请求")
        

#def export(request):
#    res_list = Order.objects.order_by('problem_type_third')
#    start_time ='2014-02-01'
#    end_time = '2014-03-01'
#    res_list = res_list.filter(create_time__gte=start_time)
#    res_list = res_list.filter(create_time__lt=end_time)
#    
#    ll = []
#    for item in res_list:
#        temp = []
#        record = OrderExtend(item, request)
#        temp.append(item.case_number)
#        temp.append(record.create_time)
#        temp.append(record.area)
#        temp.append(record.source)
#        temp.append(record.problem_type)
#        temp.append(record.status)
#        t = ','.join(temp)
#        ll.append(t)
#        
#    filename = 'export'
#    filename = filename.encode('gbk')
#    response = HttpResponse(mimetype='text/csv')  
#    response['Content-Disposition'] = 'attachment; filename=' + filename + '.csv'  
#    a  = '\n'.join(ll) 
#    a = a.encode('gbk')
#    response.content = a
#    return response
    
    
    
    
    
    
    
    
     
