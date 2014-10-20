# -*- coding:utf-8 -*-

from django.db import models

# our own lib
from software.models import Software

# 安装记录
class InstallRecord(models.Model):
    # 重新定义表名
    class Meta:
        db_table = 'install_record'
    # 部门
    department = models.CharField(max_length=32)
    # 用户姓名
    username = models.CharField(max_length=32)
    # 邮件
    mail = models.CharField(max_length=32)
    # 电话
    phone = models.CharField(max_length=20)
    # 机器SN号
    sn_number = models.CharField(max_length=20)
    # mac地址
    mac_address = models.CharField(max_length=20)
    # 安装时间
    install_time = models.DateTimeField()
    # 安装人员
    installer = models.CharField(max_length=32)
    # 变更信息
    change_info = models.CharField(max_length=64)
    # 备注信息
    comment = models.CharField(max_length=64)
    
    software = models.ForeignKey(Software) # 多对一关联
    
    