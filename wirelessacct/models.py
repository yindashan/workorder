# -*- coding:utf-8 -*-
from datetime import datetime
from django.db import models
from celery import task

# 访客帐号申请记录
    # 重新定义表名
class WirelessApplyRecord(models.Model):
    class Meta:
        db_table = 'wireless_apply_record'
    # 访客姓名
    guest_name = models.CharField(max_length=32)
    # 访客单位
    guest_unit = models.CharField(max_length=32)
    # 申请原因
    reason = models.CharField(max_length=200)
    # 生效日期
    effective_time = models.DateTimeField()
    # 失效时间
    expire_time = models.DateTimeField()
    # 数量
    number = models.IntegerField()
    # 创建时间
    create_time = models.DateTimeField()
    # 申请人(存中文)
    applicant = models.CharField(max_length=32)
    # 创建人(帐户名 如zhu.wei)
    creator = models.CharField(max_length=32)
    # 状态 0:未启用 1:正常 2:失效 3:停用
    # 注:相应状态只有在此记录被用户从页面浏览时，状态才会被修改
    status = models.IntegerField()
    # 是否已经被同步到radius数据库中
    is_sync = models.IntegerField()
    
    
# 无线路由器帐号密码
class WirelessAccount(models.Model):
    class Meta:
        db_table = 'wireless_account'
    # 用户名
    username = models.CharField(max_length=64)
    # 密码
    password = models.CharField(max_length=64)
    
    # 关联到radius数据库中的radcheck表的id
    rel_id = models.IntegerField()
    
    # 申请记录
    record = models.ForeignKey(WirelessApplyRecord) # 多对一关联
    
# 无线路由访客帐号(FreeRadius协议)
# 此表将存储在(另一个数据库中)
class RadCheck(models.Model):
    class Meta:
        db_table = 'radcheck'
    # 用户名
    username = models.CharField(max_length=64)
    # 属性
    attribute = models.CharField(max_length=64)
    # 操作
    op = models.CharField(max_length=2)
    # 值
    value = models.CharField(max_length=253)


def deal_status(item_list):
    res_list = []
    for item in item_list:
        if item.status < 2:
            if datetime.now() > item.expire_time:
                item.status = 2
                item.save()
            elif datetime.now() > item.effective_time:
                item.status = 1
                item.save()
        res_list.append(item)
    return res_list
    
def change_status(item):
    if item.status < 2:
        if datetime.now() > item.expire_time:
            item.status = 2
            item.save()
        elif datetime.now() > item.effective_time:
            item.status = 1
            item.save()
    return item    
    
# 将生效的帐号插入radius数据库的radcheck表
@task
def sync_radius():
    #print 'running....'
    curr = datetime.now()
    query_set = WirelessApplyRecord.objects.filter(is_sync=0, effective_time__lte=curr,\
        expire_time__gt=curr)
        
    # 排除停用的情况
    record_list = query_set.exclude(status = 3)
    for record in record_list:
        record.is_sync = 1
        record.save()
        
        account_list = WirelessAccount.objects.filter(record = record)
        for account in account_list:
            # 密码
            rad = RadCheck()
            rad.username = account.username
            rad.attribute = 'cleartext-Password'
            rad.op = ':='
            rad.value = account.password
            rad.save(using='radius')
            # 过期时间
            rad = RadCheck()
            rad.username = account.username
            rad.attribute = 'Expiration'
            rad.op = ':='
            rad.value = record.expire_time.strftime('%d %b %Y %H:%M:%S')
            rad.save(using='radius')
            
            account.rel_id = rad.id
            account.save()
            
        
            

    
    
    
    
    