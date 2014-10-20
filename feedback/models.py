#!/usr/bin/env python
# encoding: utf-8
'''
Created on 2013-10-21

@author: jingwen.wu
'''

from django.db import models

class Feedback(models.Model):
    '''
    反馈表
    '''

    class Meta:
        '''
        重新定义表名
        '''
        db_table = 'feedback'
    
    title = models.CharField(max_length=64)  # 标题
    content = models.TextField()  # 反馈内容
    status = models.IntegerField(default=0)  # 状态  0：提交， 1：已回复， 2：已关闭
    reporter = models.CharField(max_length=32)  # 反馈人
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)  # 创建时间，格式为'0000-00-00 00:00:00'
    
    reply_content = models.TextField()  # 推荐回复内容
    
    def __unicode__(self):
        return self.title
    
    
class Reply(models.Model):
    '''
    回复表
    '''
    
    class Meta:
        db_table = 'reply'
        
    content = models.TextField()  # 回复内容
    feedback = models.ForeignKey(Feedback)  # 外键关联反馈表
    replier = models.CharField(max_length=32)  # 回复人
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)  # 创建时间，格式为'0000-00-00 00:00:00'
    
    is_top = models.IntegerField(default=0)  # 是否被推荐。  0：未推荐，1：推荐
    
    
    
