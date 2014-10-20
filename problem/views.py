#!usr/bin/env python
# -*- coding:utf-8 -*-
#django
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect,HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import *
from django.contrib.auth import authenticate, login as auth_login ,logout as auth_logout
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required


#standard library
import json

#our own code
from problem.models import tree_structure,ProblemType
from problem.models import append_node,update_node,delete_node
from authority.decorators import permission_required


# 问题类目
@permission_required('config_manage')
def index(request): 
    return render_to_response('problem/index.html') 
    
# 问题类目树
@permission_required('config_manage')
def tree(request):
    #根节点id
    node_id = 1;
    tree_struct = tree_structure(node_id)
    node_list = []
    if tree_struct:
        node_list.append(tree_struct)
    return HttpResponse(json.dumps(node_list),mimetype="text/plain",status=200,content_type="text/plain")

# 增删改 树中的节点 
@permission_required('config_manage')
def manipulate_tree(request):
    if request.POST:
        dd = {}
        dd['status']='failure'
        action = request.POST.get('action')
        if action == 'append':
            parent_id = request.POST.get("parent_id")
            text = request.POST.get("text")
            node = append_node(parent_id,text)
            
            dd['node_id']=node.id;
        elif action == 'update':
            node_id = request.POST.get("node_id")
            text = request.POST.get("text")
            update_node(node_id,text)
            
        elif action == 'delete':
            node_id = int(request.POST.get('node_id'))
            delete_node(node_id)
            
        dd['status']='success'
        return HttpResponse(content=json.dumps(dd), content_type='text/plain')
    return HttpResponseBadRequest(u"错误请求");

# 以父节点ID搜索子节点
def search(request):
    if request.method=='GET':
        parent_id = int(request.GET.get('parent_id'))
        node_list = ProblemType.objects.filter(parent_id=parent_id, is_available=1)
        res_list = []
        for node in node_list:
            item = {}
            item['id'] = node.id
            item['text'] = node.text
            res_list.append(item)
            
        return HttpResponse(json.dumps(res_list))
    else:
        return  HttpResponseBadRequest(u"错误请求")
    

    