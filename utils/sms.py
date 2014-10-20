#!/usr/bin/env python
# *-*coding:utf-8*-*
import json
import logging, socket
import httplib, urllib
from django.conf import settings

# *****************************
# *** 注意短信内容必须是GBK编码 ***
# *****************************
def sms(contact, content):
    logger = logging.getLogger('django.notify')
    dd = {'name':settings.SMS_USER, 'password':settings.SMS_PASSWORD,
        'mobiles':contact, 'content':content.encode('gbk')}
    body = urllib.urlencode(dd)
    headers = {}
    # 打日志需要的参数
    params = 'mobile:' + contact + ' ' + content
    try:
        conn = httplib.HTTPSConnection(settings.SMS_SERVER, settings.SMS_PORT)
        conn.request("POST", settings.SERVLET_URL, body, headers)
        response = conn.getresponse() 
        # 短信通道不稳定，因此需要日志记录
        logger.info(u'发送短信成功.' + params + '\n' + response.read())
        conn.close()
        
    except socket.error,e:
        logger.error(u'发送短信失败.' + params + str(e))
    
