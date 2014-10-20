# -*- coding:utf-8 -*-
from django.db import models

# 软件信息
class Software(models.Model):
    # 重新定义表名
    class Meta:
        db_table = 'software'
    # 简写名称
    short_name = models.CharField(max_length=32)
    # 全称
    full_name = models.CharField(max_length=32)
    # 备注
    comment = models.CharField(max_length=64)
    # 许可数量
    license_count = models.IntegerField()
    # 修改时间
    modify_time = models.DateTimeField()
    
