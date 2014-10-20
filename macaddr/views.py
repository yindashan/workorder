#!usr/bin/env python
#coding: utf-8
'''
Created on 2013-9-26

@author: jingwen.wu

Mac 地址查询
'''

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

import os
from workorder.settings import  MAC_DIR

@login_required
def mac_search(request):
    '''
    Mac 地址查询
    '''
    if request.POST:
        # Mac 地址
        mac_addr = request.POST.get('mac_addr', None)
        if mac_addr == None:
            return render_to_response('macaddr/mac_search_return.html', 
                                      {'message': 1, 
                                       'mac_addr': mac_addr}, 
                                      context_instance=RequestContext(request))
        if len(mac_addr) < 12 or len(mac_addr) > 17:
            return render_to_response('macaddr/mac_search_return.html', 
                                      {'message': 2, 
                                       'mac_addr': mac_addr}, 
                                      context_instance=RequestContext(request))
    
        mac_addr = mac_addr.replace(':', '')
        mac_addr = mac_addr.replace('-', '')
        mac_addr = mac_addr.upper()
    
        dir = MAC_DIR
        
        for file in os.listdir(dir):
        
            path = os.path.join(dir, file)
            
            with open(path,'r') as mac_file:
                lines = mac_file.readlines()
                flag = -1
                for i in range(len(lines)):
                    try:
                        flag = lines[i].find(mac_addr)
                    except:
                        
                        '''
                        'utf8' codec can't decode byte 0xa0 in position 528558: invalid start byte
                        '''
                        pass
                    
                    if flag != -1:
                        return render_to_response('macaddr/mac_search_return.html', 
                                                  {'message': 3, 
                                                   'mac_addr': mac_addr}, 
                                                   context_instance=RequestContext(request))
                        
        return render_to_response('macaddr/mac_search_return.html', 
                                  {'message': 4,
                                   'mac_addr': mac_addr}, 
                                  context_instance=RequestContext(request))
    return render_to_response('macaddr/mac_search.html', 
                              {'message': 0}, 
                              context_instance=RequestContext(request))   