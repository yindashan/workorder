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


# our own code
from area.models import Area
from authority.models import Permission,area2AuthStr
from authority.decorators import permission_required


# 显示用户列表
@permission_required('config_manage')
def index(request):
    items = Area.objects.all()
    paginator = Paginator(items, 10)
    currentPage = request.POST.get('pageNum', 1)
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)
        
    return render_to_response('area/index.html',{'area_list':pager})
    
@permission_required('config_manage')
def add(request):
    if request.POST:
        area_name = request.POST.get("name")
        
        #　保存区域信息
        area = Area();
        area.name = area_name
        area.save()
        
        # 生成对应的权限字段
        p = Permission()
        p.codename = area2AuthStr(area.id)
        p.desc = area.name + u'工单管理权限'
        p.type = 4
        p.save()
        
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/area/index", "message":u'添加成功'}), mimetype='application/json')
    return render_to_response('area/add.html')

@permission_required('config_manage') 
def edit(request, area_id):
    area = None
    try:
        area = Area.objects.get(id=int(area_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'区域不存在!'}), mimetype='application/json')
    if request.POST:
        area.name = request.POST.get('name')
        area.save()

        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/area/index", "message":u'编辑成功'}), mimetype='application/json')
    return render_to_response('area/edit.html', {'area':area}) 


