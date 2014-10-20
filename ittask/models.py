#!/usr/bin/env python
# encoding: utf-8

from django.db import models
from staff.models import Staff
from celery import task
from datetime import datetime, timedelta

# our own lib
from notify.models import update_status_notify

# IT任务
class ItTask(models.Model):

    class Meta:
        '''
        重新定义表名
        '''
        db_table = 'it_task'
    # 主题
    subject = models.CharField(max_length=64)  
    # 内容
    content = models.TextField()  
    # 状态  0:进行中 1:关闭 
    status = models.IntegerField()  
    # 任务创建人-账户名
    username = models.CharField(max_length=32)  
    # 任务创建人-真实姓名
    realname = models.CharField(max_length=32) 
    
    # 创建时间，格式为'0000-00-00 00:00:00'
    create_time = models.DateTimeField()  
    # 修改时间(包括两种情况:1.备注被更新 2.原任务被修改) 
    modify_time = models.DateTimeField()  
    # 计划完成时间
    plan_finish_time = models.DateTimeField() 
    # 下一次通知时间
    notify_time = models.DateTimeField()
     
    # 更新频率
    interval = models.IntegerField() # 自动发邮件通知任务执行负责人更新备注
    
    # 最新备注
    remark = models.TextField()  
    
    # IT任务跟IT员工－多对多
    executors = models.ManyToManyField(Staff, related_name='ittasks')
    # 多对一关联
    director = models.ForeignKey(Staff) 
    
    
# 工单备注
class TaskRemark(models.Model):
    # 重新定义表名
    class Meta:
        db_table = 'it_task_remark'
    # 主键由Django生成
    # 创建时间
    create_time = models.DateTimeField()
    # 创建人(真实姓名)
    creator = models.CharField(max_length=32)
    # 备注
    comment = models.TextField()

    # 任务 
    task = models.ForeignKey(ItTask) # 多对一关联
    

# 通知IT任务的负责人更新任务的执行进度
@task
def update_notify():
    now_time = datetime.now()
    task_list = ItTask.objects.filter(status=0, notify_time__lt=now_time)
    for task in task_list:
        update_status_notify(task)
        # 下一次通知时间
        task.notify_time = task.notify_time + timedelta(days=task.interval)
        task.save()
        
    
        
    
    
    
    
    
    
    
    
    
        