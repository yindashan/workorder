# -*- coding:utf-8 -*-

# django library
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect,HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login as auth_login ,logout as auth_logout
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required

# std lib
from datetime import datetime
# our own code
from utils.constants import priority_dict
from authority.decorators import permission_required
from software.models import Software
from problem.models import ProblemType
from area.models import Area

# 提交软件安装申请
@login_required
def apply_software(request, sw_id):
    # 一级问题类目
    first_level_problem_list = ProblemType.objects.filter(level=1, is_available=1)
    # 区域
    area_list = Area.objects.all()
    sw = Software.objects.get(id=int(sw_id))
    problem_desc = u"软件安装申请:\n软件名称:%s\n" % sw.full_name
    return render_to_response('software/apply.html',{'area_list':area_list, 'priority_dict':priority_dict, 
        'user':request.user,'first_level_problem_list':first_level_problem_list,
        'auth_set':request.session["authority_set"], 'problem_desc':problem_desc}) 
    
    
# 客户申请软件安装
@login_required
def customer_index(request):
    items = Software.objects.all()
    paginator = Paginator(items, 10)
    currentPage = request.POST.get('pageNum', 1)
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)
        
    return render_to_response('software/customer_index.html',{'software_list':pager})
    
# 显示用户列表
@permission_required('software_manage')
def index(request):
    items = Software.objects.all()
    paginator = Paginator(items, 10)
    currentPage = request.POST.get('pageNum', 1)
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)
        
    return render_to_response('software/index.html',{'software_list':pager})
    
@permission_required('software_manage')
def add(request):
    if request.POST:
        item = Software()
        item.short_name = request.POST.get("short_name")
        item.full_name = request.POST.get("full_name")
        item.comment = request.POST.get("comment")
        item.license_count = int(request.POST.get("license_count"))
        item.modify_time = datetime.now()
        item.save()
        
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/software/index", "message":u'添加成功'}), mimetype='application/json')
    return render_to_response('software/add.html')

@permission_required('software_manage') 
def edit(request, sw_id):
    sw = None
    try:
        sw = Software.objects.get(id=int(sw_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'软件不存在!'}), mimetype='application/json')
    if request.POST:
        sw.short_name = request.POST.get("short_name")
        sw.full_name = request.POST.get("full_name")
        sw.comment = request.POST.get("comment")
        sw.license_count = int(request.POST.get("license_count"))
        sw.modify_time = datetime.now()
        sw.save()
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/software/index", "message":u'编辑成功'}), mimetype='application/json')
        
    return render_to_response('software/edit.html',{'software':sw}) 
         
    