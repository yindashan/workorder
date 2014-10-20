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

# stdandard library
import datetime

# our own code
from authority.decorators import permission_required
from installrecord.models import InstallRecord
from software.models import Software


@permission_required('software_manage')
def index(request):
    sw_list = Software.objects.all()
    return render_to_response('installrecord/index.html',{'sw_list':sw_list})

# 添加软件安装记录
@permission_required('software_manage')   
def edit(request, ir_id):
    record = InstallRecord.objects.get(id=ir_id)
    if request.method == 'POST':
        # 用户名
        record.username = request.POST.get('username')
        # 部门
        record.department = request.POST.get('department')
        # 机器SN号
        record.sn_number = request.POST.get('sn_number')
        # 物理地址
        record.mac_address = request.POST.get('mac_address')
        # 电话
        record.phone = request.POST.get('phone')
        # 邮件
        record.mail = request.POST.get('mail')
        # 安装人员
        record.installer = request.POST.get('installer')
        # 变更信息
        record.change_info = request.POST.get('change_info')
        # 备注
        record.comment = request.POST.get('comment')
        record.save()
        
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/installrecord/index", "message":u'编辑成功'}), 
            mimetype='application/json')
    else:
        return render_to_response('installrecord/edit.html',{'record':record})

# 添加软件安装记录
@permission_required('software_manage')   
def add(request):
    if request.method == 'POST':
        record = InstallRecord()
        # 软件ID
        sw_id = int(request.POST.get('sw_id'))
        sw = Software.objects.get(id = sw_id)
        record.software = sw
        # 用户名
        record.username = request.POST.get('username')
        # 部门
        record.department = request.POST.get('department')
        # 机器SN号
        record.sn_number = request.POST.get('sn_number')
        # 物理地址
        record.mac_address = request.POST.get('mac_address')
        # 电话
        record.phone = request.POST.get('phone')
        # 邮件
        record.mail = request.POST.get('mail')
        # 安装人员
        record.installer = request.POST.get('installer')
        # 变更信息
        record.change_info = request.POST.get('change_info')
        # 备注
        record.comment = request.POST.get('comment')
        # 安装时间
        record.install_time = datetime.datetime.now()
        record.save()
        # 软件授权数量变更
        sw.license_count = sw.license_count - 1
        sw.save()
        
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/installrecord/index", "message":u'添加成功'}), 
            mimetype='application/json')
    else:
        sw_list = Software.objects.all()
        return render_to_response('installrecord/add.html',{'sw_list':sw_list, 'user':request.user})

# 删除
@permission_required('software_manage')
def delete(request, ir_id):
    record = None
    try:
        record = InstallRecord.objects.get(id=int(ir_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'此安装记录不存在!'}), mimetype='application/json')
    # 软件授权数量变更
    sw = Software.objects.get(id = record.software.id)
    sw.license_count = sw.license_count + 1
    sw.save()
    # 删除此记录
    record.delete()

    return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/installrecord/index", "message":u'删除成功'}), mimetype='application/json')
  
@permission_required('software_manage')
def search(request):
    if request.method == 'POST':
        # 用户名
        username = request.POST.get('username')
        # 软件ID
        sw_id = request.POST.get('sw_id')
        # 安装人员
        installer = request.POST.get('installer')
        # 开始时间
        start_time = request.POST.get('start_time')
        # 结束时间
        end_time = request.POST.get('end_time')
        # 部门
        department = request.POST.get('department')
        # 机器SN号
        sn_number = request.POST.get('sn_number')
        # 物理地址
        mac_address = request.POST.get('mac_address')
        
        # FIXME 注意权限控制
        res_list = InstallRecord.objects.select_related().order_by('-install_time')
        
        if username:
            res_list = res_list.filter(username__contains=username)
            
        if sw_id:
            res_list = res_list.filter(software=sw_id)
            
        if installer:
            res_list = res_list.filter(installer__contains=installer)
        
        if start_time:
            start_time = datetime.datetime.strptime(start_time,'%Y-%m-%d')
            res_list = res_list.filter(install_time__gte=start_time)
        
        if end_time:
            # 2013-04-14
            end_time = datetime.datetime.strptime(end_time,'%Y-%m-%d')
            end_time = end_time + datetime.timedelta(days= 1)
            
            res_list = res_list.filter(install_time__lt=end_time)
            
        if department:
            res_list = res_list.filter(department__contains=department)
        if sn_number:
            res_list = res_list.filter(sn_number=sn_number)
        if mac_address:
            res_list = res_list.filter(mac_address=mac_address)
            
        paginator = Paginator(res_list, 10)
        currentPage = request.POST.get('pageNum', 1)
        try:
            pager = paginator.page(currentPage)
        except InvalidPage:
            pager = paginator.page(1)
        
        return render_to_response('installrecord/searchback.html',{'record_list':pager})
    else:
        return  HttpResponseBadRequest(u"错误请求")
    
    
    
    
    
    