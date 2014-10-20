# -*- coding:utf-8 -*-

# django library
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login as auth_login , logout as auth_logout
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required
from django.db.models import Q

# std lib
from datetime import datetime, timedelta 
# our own code
from authority.decorators import permission_required
from ittask.models import ItTask, TaskRemark
from staff.models import Staff
from utils.constants import ittask_status_dict, update_period_dict
from notify.models import ittask_create_notify

    
@permission_required('ittask_watch')
def index(request):
    auth_set = request.session["authority_set"]
    return render_to_response('ittask/index.html',{'auth_set':auth_set,\
        'ittask_status_dict':ittask_status_dict})

# 我的项目       
@permission_required('ittask_deal')
def mytask(request):
    uname = request.user.username
    id_list = ItTask.objects.filter(Q(director__accountname=uname) | \
        Q(executors__accountname=uname)).values('id').distinct().values_list('id', flat=True)
        
    items = ItTask.objects.filter(id__in=id_list,status=0).\
        select_related().order_by('create_time')
    paginator = Paginator(items, 10)
    currentPage = request.POST.get('pageNum', 1)
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)
        
    return render_to_response('ittask/mytask.html', {'task_list':pager,
        'ittask_status_dict':ittask_status_dict})

# 我的历史项目
@permission_required('ittask_deal')
def my_history(request):
    return render_to_response('ittask/myhistory.html')
    
# 我的历史项目--对应的搜索
@permission_required('ittask_deal')
def my_search(request):
    uname = request.user.username
    id_list = ItTask.objects.filter(Q(director__accountname=uname) | \
        Q(executors__accountname=uname)).values('id').distinct().values_list('id', flat=True)
        
    res_list = ItTask.objects.filter(id__in=id_list,status=1).\
        select_related().order_by('create_time')
    
    # 主题
    subject = request.POST.get('subject')
    # 提交人
    submitor = request.POST.get('submitor')
    # 项目负责人
    director = request.POST.get('director')
    # 开始时间
    start_time = request.POST.get('start_time')
    # 结束时间
    end_time = request.POST.get('end_time')
    
    if subject:
        res_list = res_list.filter(subject__contains=subject)
        
    if submitor:
        res_list = res_list.filter(realname__contains=submitor)
        
    if director:
        res_list = res_list.filter(director__realname__contains=director)
    
    if start_time:
        start_time = datetime.strptime(start_time, '%Y-%m-%d')
        res_list = res_list.filter(create_time__gte=start_time)
    
    if end_time:
        # 2013-04-14
        end_time = datetime.strptime(end_time, '%Y-%m-%d')
        end_time = end_time + timedelta(days=1)
        
        res_list = res_list.filter(create_time__lt=end_time)
    
    paginator = Paginator(res_list, 10)
    currentPage = request.POST.get('pageNum', 1)
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)
        
    return render_to_response('ittask/mysearch.html', {'task_list':pager,
        'ittask_status_dict':ittask_status_dict})
    
    
@permission_required('ittask_watch')
def search(request):
    if request.method == 'POST':
        # 主题
        subject = request.POST.get('subject')
        # 状态
        status = request.POST.get('status')
        # 任务负责人
        director = request.POST.get('director')
        # 开始时间
        start_time = request.POST.get('start_time')
        # 结束时间
        end_time = request.POST.get('end_time')

        
        # FIXME 注意权限控制
        res_list = ItTask.objects.select_related().order_by('status','-modify_time')
        
        if subject:
            res_list = res_list.filter(subject__contains=subject)
            
        if status:
            res_list = res_list.filter(status=status)
            
        if director:
            res_list = res_list.filter(director__realname__contains=director)
        
        if start_time:
            start_time = datetime.strptime(start_time, '%Y-%m-%d')
            res_list = res_list.filter(create_time__gte=start_time)
        
        if end_time:
            # 2013-04-14
            end_time = datetime.strptime(end_time, '%Y-%m-%d')
            end_time = end_time + timedelta(days=1)
            
            res_list = res_list.filter(create_time__lt=end_time)
            
            
        paginator = Paginator(res_list, 10)
        currentPage = request.POST.get('pageNum', 1)
        try:
            pager = paginator.page(currentPage)
        except InvalidPage:
            pager = paginator.page(1)
        
        return render_to_response('ittask/searchback.html', {'task_list':pager,
            'ittask_status_dict':ittask_status_dict, 'user':request.user})
    else:
        return  HttpResponseBadRequest(u"错误请求")
    
@permission_required('ittask_add')
def add(request):
    if request.POST:
        task = ItTask()
        task.subject = request.POST.get("subject")
        task.content = request.POST.get("content")
        # 状态  0:进行中 1:关闭 
        task.status = 0
        # 任务创建人-账户名
        task.username = request.user.username
        # 任务创建人-真实姓名
        task.realname = request.user.userprofile.realname
        now_time = datetime.now()
        task.create_time = now_time
        task.modify_time = now_time
        task.plan_finish_time = request.POST.get("plan_finish_time")
        task.interval = int(request.POST.get("interval"))
        task.notify_time = (now_time + timedelta(days=task.interval)).strftime('%Y-%m-%d 09:00:00')
        # 负责人
        task.director = Staff.objects.get(id=int(request.POST.get("director")))
        task.remark = '暂无备注'
        task.save()
        # 实施者　
        id_list = request.POST.getlist('executors')
        for item in id_list:
            task.executors.add(int(item))
        
        # 邮件通知相关人员
        ittask_create_notify.delay(task)
        
        return HttpResponse(simplejson.dumps({"statusCode":200, "url": "/ittask/index", "message":u'添加成功'}), mimetype='application/json')
    else:
        staff_list = Staff.objects.filter(is_deleted=0)
        update_period_list = sorted(update_period_dict.items(), key=lambda t: t[0])
        return render_to_response('ittask/add.html', {'update_period_list':update_period_list, 'staff_list':staff_list})

# 关闭
@permission_required('ittask_add')
def close(request, ittask_id):
    task = None
    try:
        task = ItTask.objects.get(id=int(ittask_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode":400, "message":u'此IT任务不存在!'}), mimetype='application/json')
    
    # 状态  0:进行中 1:关闭 
    task.status = 1
    task.modify_time = datetime.now()
    task.save()
    
    return HttpResponse(simplejson.dumps({"statusCode":200, "url": "/ittask/index", "message":u'成功关闭'}), mimetype='application/json')

# 查看
@permission_required('ittask_watch')
def watch(request, ittask_id):
    task = ItTask.objects.get(id=int(ittask_id))
    # 当前登录用户是否有权限对此任务进行备注
    name_set = set()
    # 任务提交人
    name_set.add(task.username)
    # 任务负责人
    name_set.add(task.director.accountname)
    # 实施人
    print type(task.executors.all)
    for item in task.executors.all():
        name_set.add(item.accountname)
    
    permit_comment_flag = False
    if request.user.username in name_set and task.status != 1:
        permit_comment_flag = True
    
    remark_list = TaskRemark.objects.filter(task=task).order_by('create_time')
    staff_list = Staff.objects.filter(is_deleted=0)
    # 实施人
    ll = []
    for staff in task.executors.all():
        ll.append(staff.realname)
    
    return render_to_response('ittask/watch.html', \
        {'permit_comment_flag':permit_comment_flag, 'remark_list':remark_list, \
        'task':task, 'update_period_dict':update_period_dict,
        'staff_list':staff_list, 'executors':','.join(ll)}) 

# 备注
@permission_required('ittask_watch')
def remark_add(request, ittask_id):
    task = ItTask.objects.get(id=int(ittask_id))
    
    remark = TaskRemark()
    remark.comment = request.POST.get('remark')
    remark.task = task
    remark.creator = request.user.userprofile.realname
    remark.create_time = datetime.now()
    remark.save()
    
    task.remark = remark.comment
    task.modify_time = datetime.now()
    task.save()
    
    return HttpResponse(simplejson.dumps({"statusCode":200, "url": "/ittask/index", "message":u'备注成功'}),
        mimetype='application/json')
    
@permission_required('ittask_add')
def edit(request, ittask_id):
    task = ItTask.objects.get(id=int(ittask_id))
    if request.method == 'POST':
        task.subject = request.POST.get("subject")
        task.content = request.POST.get("content")
        task.modify_time = datetime.now()
        task.plan_finish_time = request.POST.get("plan_finish_time")
        task.interval = int(request.POST.get("interval"))
        # 负责人
        task.director = Staff.objects.get(id=int(request.POST.get("director")))
        task.save()
        # 实施者　
        id_list = request.POST.getlist('executors')
        task.executors.clear()
        for item in id_list:
            task.executors.add(int(item))
        
        return HttpResponse(simplejson.dumps({"statusCode":200, "url": "/ittask/index", "message":u'编辑成功'}),
            mimetype='application/json')
    else:
        selected_id_list = []
        for staff in task.executors.all():
            selected_id_list.append(staff.id)
        staff_list = Staff.objects.filter(is_deleted=0)
        update_period_list = sorted(update_period_dict.items(), key=lambda t: t[0])
        return render_to_response('ittask/edit.html', {'task':task, 'selected_id_list':selected_id_list, \
            'update_period_list':update_period_list, 'staff_list':staff_list}) 
            
            
@permission_required('ittask_watch')
def sedit(request, ittask_id):
    task = ItTask.objects.get(id=int(ittask_id))
    if request.method == 'POST':
        task.modify_time = datetime.now()
        task.save()
        # 实施者　
        id_list = request.POST.getlist('executors')
        task.executors.clear()
        for item in id_list:
            task.executors.add(int(item))
        
        return HttpResponse(simplejson.dumps({"statusCode":200, "url": "/ittask/mytask", "message":u'编辑成功'}),
            mimetype='application/json')
    else:
        selected_id_list = []
        for staff in task.executors.all():
            selected_id_list.append(staff.id)
        staff_list = Staff.objects.filter(is_deleted=0)
        update_period_list = sorted(update_period_dict.items(), key=lambda t: t[0])
        return render_to_response('ittask/sedit.html', {'task':task, 'selected_id_list':selected_id_list, \
            'update_period_list':update_period_list, 'staff_list':staff_list}) 
         
    
