# -*- coding:utf-8 -*-
from django.db import models
from staff.models import Staff

# 高管名单
class Executive(models.Model):
    # 重新定义表名
    class Meta:
        db_table = 'senior_executive'
    # 用户名
    realname = models.CharField(max_length=64)
    # 账户名
    accountname = models.CharField(max_length=32)
    # 邮件
    email = models.CharField(max_length=64)
    # 部门
    department = models.CharField(max_length=128)
    # 职务
    job = models.CharField(max_length=64)
    
    # 第一工程师id
    first_engineer_id = models.IntegerField()
    # 第二工程师id
    second_engineer_id = models.IntegerField()
    
# 高管名单扩展类
class ExecutiveExtend():
    def __init__(self,s):
        self.id = s.id
        self.realname = s.realname
        self.accountname = s.accountname
        self.email = s.email
        self.department = s.department
        self.job = s.job
        self.first_engineer = Staff.objects.get(id=s.first_engineer_id)
        self.second_engineer = Staff.objects.get(id=s.second_engineer_id)
        
        
    
    