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


# std lib
import random

# our own code
from wirelessacct.models import WirelessApplyRecord, WirelessAccount
from wirelessacct.models import deal_status, RadCheck, change_status
from datetime import timedelta, datetime
from authority.decorators import permission_required
from utils.utils import randPassword
from utils.constants import wireless_status_dict

@permission_required('wireless_manage')
def index(request):
    item_list = WirelessApplyRecord.objects.order_by("-id")
    paginator = Paginator(item_list, 10)
    currentPage = request.POST.get('pageNum', 1)
    
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)
        
    # 修改记录的状态
    pager.object_list = deal_status(pager.object_list)
    return render_to_response("wirelessacct/index.html",{"record_list":pager,\
        'wireless_status_dict':wireless_status_dict})
        
@login_required     
def add(request):
    if request.POST:
        duration_day = int(request.POST.get("duration_day"))
        duration_hour = int(request.POST.get("duration_hour"))
        
        record = WirelessApplyRecord()
        # 访客姓名
        record.guest_name = request.POST.get("guest_name")
        # 访客单位
        record.guest_unit = request.POST.get("guest_unit")
        # 申请原因
        record.reason = request.POST.get("reason")
        # 申请数量
        record.number = int(request.POST.get("number"))
        # 生效日期
        effective_time = request.POST.get("effective_time")
        record.effective_time = datetime.strptime(effective_time,'%Y-%m-%d %H:%M')
        # 失效时间
        record.expire_time = record.effective_time + timedelta(days=duration_day, hours=duration_hour)
        # 状态
        record.status = 0
        # 创建时间
        record.create_time = datetime.now()
        # 记录申请人
        record.applicant = request.user.userprofile.realname
        # 创建人
        record.creator = request.user.username
        # 是否被同步
        record.is_sync = 0
        record.save()
        
        # guest无线帐号
        for i in range(record.number):
            item = WirelessAccount()
            item.record = record
            # 8位随机数字
            item.username = random.randint(10000000, 100000000 -1)
            # 8位随机密码
            item.password = randPassword(8, False)
            item.rel_id = -1
            item.save()
        
        url = "/wirelessacct/detail/%s/" % str(record.id)
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": url, "message":u'申请成功'}), 
            mimetype='application/json')
    return render_to_response('wirelessacct/add.html', {'hours':range(24)})

@login_required     
def detail(request, record_id):
    record = WirelessApplyRecord.objects.get(id=record_id)
    record = change_status(record)
    # 账户列表
    account_list = WirelessAccount.objects.filter(record=record)
    return render_to_response("wirelessacct/detail.html",{"record":record,\
        'account_list':account_list,'wireless_status_dict':wireless_status_dict})

@permission_required('wireless_manage')     
def stop(request, record_id):
    record = WirelessApplyRecord.objects.get(id=record_id)
    
    if record.is_sync == 1:
        # 账户列表
        account_list = WirelessAccount.objects.filter(record=record)
        for account in account_list:
            item_list = RadCheck.objects.using('radius').filter(id=account.rel_id)
            for item in item_list:
                item.value = datetime.now().strftime('%d %b %Y %H:%M:%S')
                item.save(using='radius')
                
    record.status = 3
    record.save()
    return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/wirelessacct/index", "message":u'停用成功'}), 
            mimetype='application/json')
    
# 申请历史
@login_required  
def history(request):
    item_list = WirelessApplyRecord.objects.filter(creator=request.user.username).order_by("-id")
    paginator = Paginator(item_list, 10)
    currentPage = request.POST.get('pageNum', 1)
    
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)
        
    # 修改记录的状态
    pager.object_list = deal_status(pager.object_list)
    return render_to_response("wirelessacct/history.html",{"record_list":pager,\
        'wireless_status_dict':wireless_status_dict})
    
    
    
    
    
    
