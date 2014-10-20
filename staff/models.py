# -*- coding:utf-8 -*-
from django.db import models
from area.models import Area

# IT员工
class Staff(models.Model):
    # 重新定义表名
    class Meta:
        db_table = 'it_staff'
    # 账户名
    accountname = models.CharField(max_length=32)
    # 用户名
    realname = models.CharField(max_length=64)
    # 是否有效 0:无效,1:有效 
    is_available = models.IntegerField()
    # 电子邮件
    email = models.CharField(max_length=64)
    # 手机号码
    phone = models.CharField(max_length=32)
    # 是否删除 0:未删除，1:已删除
    is_deleted = models.IntegerField()
    # 权重  1 ~ 10
    weight = models.IntegerField()
    
    # 所属区域
    area = models.ForeignKey(Area) # 多对一关联
    
    
    