# -*- coding:utf-8 -*-
from django.db import models

# our own code


# 工单
class Area(models.Model):
    # 重新定义表名
    class Meta:
        db_table = 'area'
    # 主键由Django生成
    # 名称
    name = models.CharField(max_length=32) 
    


