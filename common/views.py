#!usr/bin/env python
#coding: utf-8
#django
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import *
from django.contrib.auth import authenticate, login as auth_login , logout as auth_logout
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required

#standard library
import datetime

#our own code
from log.models import Log 
from dynamicconfig.models import login_ldap, search_user
from account.models import getUser, UserProfile
from order.models import Order
from staff.models import Staff
from area.models import Area
from utils.constants import staff_status_dict

# 首页  / 系统管理
@login_required
def index(request): 
    # 部分应用中监控项读权限
    auth_set = request.session["authority_set"]
    user = getUser(request.user.id)  
    
    today = datetime.datetime.now()  # 取得今天日期
    staff_list = Staff.objects.filter(is_available=1, is_deleted=0).order_by("area")  # IT员工列表
    order_list = Order.objects.filter(create_time__year=today.year, create_time__month=today.month, create_time__day=today.day)  # 工单列表
    area_list = Area.objects.all()  # 办公区列表
    
    # IT员工状态列表
    # 格式：[{办公区, 日期, 人员数, 员工:[{名字, 已处理工单数, 处理中工单数, 状态}, {...}, ...]}, {...}, {...}]
    staff_status_list = []
    for area in area_list:
        area_name = area.name
        staff_count = staff_list.filter(area_id=area.id).count()
        staff_status_list.append({'area': area_name, 'date': today.strftime("%Y-%m-%d"), 'staff_count': staff_count, 'staff': []})

        for staff in staff_list:
            if staff.area_id == area.id:
                realname = staff.realname
                dealed_count = order_list.filter(dealer_realname=realname, status__in=[3,5]).count()
                dealing_count = order_list.filter(dealer_realname=realname, status__in=[2,4]).count()
                if dealing_count > 6:
                    status = 3
                elif dealing_count > 3:
                    status = 2
                elif dealing_count > 0:
                    status = 1
                else:
                    status = 0
                staff_status_list[len(staff_status_list)-1]['staff'].append({'realname': realname, 'dealed': dealed_count, 'dealing': dealing_count, 'status': status, 'status_desc': staff_status_dict[status]})
        
    return render_to_response('common/index.html', {'user':user, 'auth_set':auth_set, 'staff_status_list':staff_status_list}) 

# 跳转到登录页
def loginpage(request):
    # 登录成功跳转到用户的原请求页
    jump_to = request.GET.get('next')
    if not jump_to:
        jump_to = '/'
    return render_to_response('common/login.html',
                              {'next':jump_to},
                              context_instance=RequestContext(request))
    
# 登录    
def login(request):
    if request.POST:
        username = request.POST.get("username")
        password = request.POST.get("password")
        jump_to = request.POST.get("next")
        # 验证用户名密码
        res = login_core(request, username.strip(), password.strip())
        if res:
            # 检查用户的角色
            roles = request.user.role_set.all()
            # 权限集合　元素为字符串
            auth_set = set()
            permission_id_list = []
            # 因为角色而得到的权限
            for role in roles:
                for p in role.permissions.all():
                    auth_set.add(p.codename)
                    permission_id_list.append(p.id)
            # 其它权限
            for p in request.user.permission_set.all():
                auth_set.add(p.codename)
                permission_id_list.append(p.id)
                
            request.session["authority_set"] = auth_set
            request.session["permission_id_list"] = permission_id_list
            # 获取登录IP
            RemoteIp = request.META.get('REMOTE_ADDR')
            Log(username=request.user.username, log_type=0, content="execute login user:" + request.user.username + " ip:" + RemoteIp + " success!", level=1).save()
            #重定向到首页
            return HttpResponseRedirect(jump_to)
        else:
            Log(username=username, content="execute login user error!", level=1).save()
            return render_to_response("common/login.html", { "message":u"登录失败", 'next':'/'}, context_instance=RequestContext(request))
     
    else:
        return  HttpResponseBadRequest(u"错误请求")

# 登录核心方法 注意特殊用户 admin
def login_core(request, username, password):
    ret = False
    
    if username == 'admin':
        # 特殊用户　admin
        user = authenticate(username=username, password=password)
    else:
        if password == '':
            return False
        # LDAP验证
        if not login_ldap(username, password):
            return False
            
        # 检查此用户是否存在，如果不存在,则自动插入用户记录
        res = User.objects.filter(username=username)
        if not res:
            # 从LDAP获取用户信息
            dd = search_user(username)[0]
            password = make_password(username, salt=None, hasher='default')
            user = User(username=username, password=password, email=dd['mail'])
            user.save()
            # 用户附加信息
            profile = UserProfile()
            profile.department = dd['department']
            profile.phone = dd['phone']
            profile.realname = dd['cn']
            profile.user = user
            profile.save()
        
        # 这里请注意   *** password=username ***
        user = authenticate(username=username, password=username)
            
    # 登陆核心方法
    if user:
        if user.is_active:
            auth_login(request, user)
            ret = True
        else:
            messages.add_message(request, messages.INFO, _(u'用户没有激活'))
    else:
        messages.add_message(request, messages.INFO, _(u'用户不存在'))
    return ret

@login_required
def logout(request):
    username = request.user.username
    # 注销
    auth_logout(request)
    Log(username=username, log_type=0, content="execute logout user success!", level=1).save()
    return render_to_response("common/login.html", {'next':'/'}, context_instance=RequestContext(request))
    
# 通用的函数，表示相应处理操作已成功
@login_required
def success(request):

    return render_to_response("common/success.html")
   

