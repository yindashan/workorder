# -*- coding:utf-8 -*-
from utils.mail import send_mail
from utils.sms import sms
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from problem.models import getProblemType
from staff.models import Staff
from django.template import Context, Template
from utils.constants import priority_dict
from staff.models import Staff
from celery import task

# ----------发送给申报人------------
# 1.派发工单提醒
@task
def distribute_customer(order):
    # 1) 生成邮件内容
    # 工程师的手机号
    engineer = Staff.objects.get(accountname=order.dealer_accountname)
    content = render_to_string('notify/distribute_customer.html', {'order': order, 'engineer_phone':engineer.phone, 
        'service_address':settings.SERVICE_ADDRESS})
    # 2) 发送邮件
    send_mail(u'IT工单系统', order.email, u'派发工单提醒', content)
    
# 2.转发工单提醒
@task
def retransmission_customer(order):
    # 1) 生成邮件内容
    # 工程师的手机号
    engineer = Staff.objects.get(accountname=order.dealer_accountname)
    content = render_to_string('notify/retransmission_customer.html', {'order': order, 'engineer_phone':engineer.phone,
        'service_address':settings.SERVICE_ADDRESS})
    # 2) 发送邮件
    send_mail(u'IT工单系统',order.email, u'转发工单提醒', content)
    
# 3.工单已解决&等待评价提醒
@task
def wait_appraise_customer(order):
    # 1) 生成邮件内容　
    # 工程师的手机号
    engineer = Staff.objects.get(accountname=order.dealer_accountname)
    content = render_to_string('notify/wait_appraise_customer.html', 
            {'order': order,'service_address':settings.SERVICE_ADDRESS, 'engineer_phone':engineer.phone})
    # 2) 发送邮件
    send_mail(u'IT工单系统',order.email, u'工单已解决&等待评价提醒', content)

# 4.工单被取消
@task
def cancel_customer(order, user, reason):
    # 1) 生成邮件内容　
    # 工程师的手机号
    content = render_to_string('notify/cancel_customer.html', 
            {'order': order, 'reason':reason, 'user':user})
    # 2) 发送邮件
    send_mail(u'IT工单系统',order.email, u'工单取消通知', content)

# ----------发送给IT工程师------------
# 1.工单派发
# ----------发送给申报人------------
# 1.派发工单提醒
@task
def distribute_engineer(order):
    # 1) 生成邮件内容
    # 提交人
    submiter = User.objects.get(username=order.creator).userprofile.realname
    # 问题类别
    problem_type = getProblemType(order.problem_type_third)
    # 动作
    operation = u'分派'
    content = render_to_string('notify/distribute_engineer.html', {'order': order, 
        'submiter':submiter, 'problem_type':problem_type, 'operation':operation})
        
    staff = Staff.objects.get(accountname=order.dealer_accountname)
    # 2) 发送邮件
    send_mail(u'IT工单系统',staff.email, u'派发工单提醒', content)

# 2.工单转发
@task
def retransmission_engineer(order):
    # 1) 生成邮件内容
    # 提交人
    submiter = User.objects.get(username=order.creator).userprofile.realname
    # 问题类别
    problem_type = getProblemType(order.problem_type_third)
    # 动作
    operation = u'转发'
    content = render_to_string('notify/distribute_engineer.html', {'order': order, 
        'submiter':submiter, 'problem_type':problem_type, 'operation':operation})
    
    staff = Staff.objects.get(accountname=order.dealer_accountname)
    # 2) 发送邮件
    send_mail(u'IT工单系统',staff.email, u'工单转发提醒', content)
    
@task 
def sms_notify(order):
    # 1) 生成短信内容
    t = Template(u"工单号：{{order.case_number}}，用户：{{order.realname}}，办公区：{{order.area.name}}，电话：{{order.phone}}，部门：{{order.department}}，优先级：{{priority}}。请及时联系用户并协助处理。")
    priority = priority_dict[order.priority_level]
    c = Context({'order': order, 'priority':priority})
    content = t.render(c)
    
    # 2) 发送短信
    # 处理人手机号
    staff = Staff.objects.get(accountname = order.dealer_accountname)
    sms(staff.phone, content)

@task 
def ittask_create_notify(task):
    # 1) 邮件内容
    ll = []
    to_addrs = []
    for staff in task.executors.all():
        ll.append(staff.realname)
        to_addrs.append(staff.email)
    
    content = render_to_string('notify/ittask_create.html', 
        {'task':task,'executors':','.join(ll)})
    
    to_addrs.append(task.director.email)
    # 2) 发送邮件
    send_mail(u'IT工单系统', to_addrs, u'IT项目创建通知', content)
    
# 通知IT任务的负责人修改任务执行的最新状态
def update_status_notify(task):
    # 1) 邮件内容
    ll = []
    for staff in task.executors.all():
        ll.append(staff.realname)
    content = render_to_string('notify/ittask_update_status.html',
        {'task':task,'executors':','.join(ll)})
    
    # 2) 发送邮件
    send_mail(u'IT工单系统',task.director.email, u'IT项目更新提醒', content)
    
    


