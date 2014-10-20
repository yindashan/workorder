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
from authority.models import Permission
from role.models import Role
from log.models import Log
from utils.constants import permission_type_dict
from authority.decorators import permission_required

# 显示用户列表
@permission_required('role_manage')
def index(request):
    roles = Role.objects.all()
    paginator = Paginator(roles, 10)
    currentPage = request.POST.get('pageNum', 1)
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)
        
    return render_to_response('role/index.html',{'role_list':pager}, context_instance=RequestContext(request))

# 删除记录
@permission_required('role_manage')
def delete(request, role_id):
    role = None
    try:
        role = Role.objects.get(id=int(role_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'此角色不存在!'}), mimetype='application/json')
    # 删除角色和人的关联关系
    role.users.clear()
    # 删除角色和权限的关联关系
    role.permissions.clear()
    # 删除此角色
    role.delete()
    # 日志
    Log(username=request.user.username,log_type=2,relate_id=role.id,content="execute delete role " + role.name + " success!", level=1).save()
    return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/role/index", "message":u'删除成功'}), mimetype='application/json')
   
@permission_required('role_manage')
def add(request):
    pdict = {}
    for key in permission_type_dict:
        pdict[permission_type_dict[key]]=Permission.objects.filter(type=key).order_by('id')
    
    if request.POST:
        role_name = request.POST.get("role_name")
        role_desc = request.POST.get("role_desc")
        permission_id_list = request.POST.getlist("permission_id")
        #　保存角色信息
        role = Role();
        role.name = role_name
        role.desc = role_desc
        role.save()
        # 保存角色和权限对应关系
        for pid in permission_id_list:
            role.permissions.add(pid)
        
        # 日志
        Log(username=request.user.username,log_type=2,relate_id=role.id,content="execute add role " + role.name + " success!", level=1).save()
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/role/index", "message":u'添加成功'}), mimetype='application/json')
    return render_to_response('role/add.html',{'pdict':pdict},context_instance=RequestContext(request))

# 编辑
@permission_required('role_manage')
def edit(request, role_id):
    pdict = {}
    for key in permission_type_dict:
        pdict[permission_type_dict[key]]=Permission.objects.filter(type=key).order_by('id')
    role = None
    try:
        role = Role.objects.get(id=int(role_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'此角色不存在!'}), mimetype='application/json')
    
    permission_id_list = [] 
    for p in role.permissions.all():
        permission_id_list.append(p.id)
    
    if request.POST:
        role_name = request.POST.get("role_name")
        role_desc = request.POST.get("role_desc")
        permission_id_list = request.POST.getlist("permission_id")
        #保存角色信息
        role.name = role_name
        role.desc = role_desc
        role.save()
        # 保存角色和权限对应关系
        role.permissions.clear()
        for pid in permission_id_list:
            role.permissions.add(pid)
        
        # 日志
        Log(username=request.user.username,log_type=2,relate_id=role.id,content="execute edit role " + role.name + " success!", level=1).save()
        return HttpResponse(simplejson.dumps({"statusCode":200,"url": "/role/index", "message":u'编辑成功'}), mimetype='application/json')  
    return render_to_response('role/edit.html', {"pdict":pdict,"role": role,"permission_id_list":permission_id_list},context_instance=RequestContext(request))
    
    
    