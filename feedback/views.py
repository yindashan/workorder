#!/usr/bin/env python
# encoding: utf-8
'''
Created on 2013-10-21

@author: jingwen.wu

反馈信息操作
'''

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.core.paginator import Paginator, InvalidPage
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
import time

# our own code
from log.models import Log
from feedback.models import Feedback, Reply
from utils.constants import feedback_status_dict
from utils.mail import send_mail
from django.conf import settings

@login_required
def index(request):
    '''
    显示反馈信息列表
    '''
    auth_set = request.session["authority_set"]    
    feedbacks = Feedback.objects.order_by('-create_time')
    feedbacks = __rn2br_feedback(feedbacks)
    paginator = Paginator(feedbacks, 10)
    currentPage = request.POST.get('pageNum', 1)
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)
    return render_to_response('feedback/index.html',
                              {'feedback_list': pager,
                               'feedback_status_dict': feedback_status_dict,
                               'auth_set': auth_set},
                              context_instance=RequestContext(request))

@login_required
def add(request):
    '''
    新增反馈信息
    '''    
    if request.POST:
        
        title = request.POST.get('title', None)
        content = request.POST.get('content', None)         
        
        feedbacks = Feedback.objects.filter(title__iexact=title)
        if feedbacks: 
            return HttpResponse(simplejson.dumps({"statusCode": 400,
                                                  "message": u'此主题的反馈信息已存在，请查看'}),
                                mimetype='application/json')
        
        feedback = Feedback(title=title, content=content,
                            reporter=request.user.userprofile.realname)    
        feedback.save()
        # 发送邮件安
        email_content = render_to_string('feedback/to_IT_email.html',
                                         {'feedback': feedback})
        
        send_mail(u'IT总监绿色通道', settings.IT_HEAD_EMAIL, u'反馈信息提醒', email_content)    
        
        Log(username=request.user.username,
            content=u'新增反馈信息：‘' + title + u'’。',
            level=1).save()
        return HttpResponse(simplejson.dumps({'statusCode': 200,
                                              'url': '/feedback/index',
                                              'message': u'反馈信息‘' + title + u'’添加成功'}),
                            mimetype='application/json')
    return render_to_response('feedback/add.html',
                              context_instance=RequestContext(request))

@login_required
def edit(request, feedback_id):
    '''
    编辑反馈信息
    '''
    feedback = None
    try:
        feedback = Feedback.objects.get(id=int(feedback_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode": 400,
                                              "message": u'此反馈信息不存在!'}),
                            mimetype='application/json')
    
    if request.POST:
        
        content = request.POST.get('content', None)

        if content != feedback.content:
            Log(username=request.user.username,
                content=u'修改反馈信息‘' + feedback.title + u'’，的内容。',
                level=1).save()
            feedback.content = content
        feedback.save()
        return HttpResponse(simplejson.dumps({'statusCode': 200,
                                              'url': 'feedback/index',
                                              'message': u'反馈信息‘' + feedback.title + u'’编辑成功'}),
                            mimetype='application/json')
    return render_to_response('feedback/edit.html',
                              {'feedback': feedback},
                              context_instance=RequestContext(request))

@login_required
def close(request, feedback_id):
    '''
    关闭反馈信息
    '''
    feedback = None
    try:
        feedback = Feedback.objects.get(id=int(feedback_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode": 400,
                                              "message": u'此反馈信息不存在!'}),
                            mimetype='application/json')
    Log(username=request.user.username,
        content=u'关闭反馈信息‘' + feedback.title + u'’。',
        level=1).save()
    feedback.status = 2
    feedback.save()
    return HttpResponse(simplejson.dumps({"statusCode": 200,
                                          "url": "/feedback/index",
                                          "message": u'关闭反馈信息‘' + feedback.title + u'’。'}),
                        mimetype='application/json')
 

@login_required
def reply(request, feedback_id): 
    '''
    回复反馈信息
    '''
    auth_set = request.session["authority_set"]
    feedback = None
    try:
        feedback = Feedback.objects.get(id=int(feedback_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode": 400,
                                              "message": u'此反馈信息不存在!'}),
                            mimetype='application/json')
            
    reply_list = Reply.objects.filter(feedback_id=int(feedback_id)).order_by('-create_time')
    reply_list = __rn2br_reply(reply_list)
    paginator = Paginator(reply_list, 50)
    currentPage = request.POST.get('pageNum', 1)
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)    
        
        
    if request.method == 'POST':
        
        content = request.POST.get('content', None)
        reply = Reply(content=content, feedback=feedback,
                      replier=request.user.userprofile.realname)
        reply.save()  
        
        if feedback.status != 1:
            feedback.status = 1
            feedback.save()
            
        Log(username=request.user.username,
            content=u'回复反馈信息‘' + feedback.title + u'’，内容‘' + reply.content[0:10] + u'……’。',
            level=1).save()            
        return HttpResponse(simplejson.dumps({'statusCode': 200,
                                              'url': 'feedback/reply/' + feedback_id + '/',
                                              'message': u'反馈信息‘' + feedback.title + u'’回复成功'}),
                            mimetype='application/json')
    return render_to_response('feedback/reply.html',
                              {'feedback': feedback, 'reply_list': pager,
                               'auth_set': auth_set},
                              context_instance=RequestContext(request))
 
    
@login_required
def detail(request, feedback_id):  
    '''
    查看反馈信息
    ''' 
    auth_set = request.session["authority_set"]
    feedback = None
    try:
        feedback = Feedback.objects.get(id=int(feedback_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode": 400,
                                              "message": u'此反馈信息不存在!'}),
                            mimetype='application/json')
        
    reply_list = Reply.objects.filter(feedback_id=int(feedback_id)).order_by('-create_time')
    reply_list = __rn2br_reply(reply_list)
    paginator = Paginator(reply_list, 50)
    currentPage = request.POST.get('pageNum', 1)
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)    
    return render_to_response('feedback/detail.html',
                              {'feedback': feedback, 'reply_list': pager,
                               'auth_set': auth_set},
                              context_instance=RequestContext(request))


@login_required
def reply_top(request, reply_id):  
    '''
    查看反馈信息
    ''' 
    reply = None
    try:
        reply = Reply.objects.get(id=int(reply_id))
    except BaseException:
        return HttpResponse(simplejson.dumps({"statusCode": 400,
                                              "message": u'此回复信息不存在!'}),
                            mimetype='application/json')
    
    # 已被推荐的回复置位“未推荐”
    try:
        reply_top = Reply.objects.get(feedback_id=reply.feedback.id,
                                      is_top=1)
        reply_top.is_top = 0
        reply_top.save()
    except BaseException:
        pass
    
    reply.feedback.reply_content = reply.content
    reply.feedback.save()
    reply.is_top = 1
    reply.save()
    Log(username=request.user.username,
        content=u'为反馈信息‘' + reply.feedback.title + u'’推荐回复‘' + reply.content[0:10] + u'……’。',
        level=1).save()      
    return HttpResponse(simplejson.dumps({'statusCode': 200,
                                          'url': 'feedback/index',
                                          'message': u'推荐回复信息‘' + reply.content + u'’成功'}),
                        mimetype='application/json')


def  __rn2br_feedback(feedbacks):
    '''
    将反馈文本内容中的 \r\n 替换为  <br>
    '''
    for feedback in feedbacks:
        feedback.content = feedback.content.replace("\r\n", "<br>")
        feedback.reply_content = feedback.reply_content.replace("\r\n", "<br>")
    return feedbacks

def  __rn2br_reply(reply_list):
    '''
    将文本内容中的
    '''
    for reply in reply_list:
        reply.content = reply.content.replace("\r\n", "<br>")
    return reply_list
