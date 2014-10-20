# -*- coding:utf-8 -*-

# django library
from django.db import models

# stdandard library
import ldap


# LDAP 
class LDAPConf(models.Model):
    #重新定义表名
    class Meta:
        db_table = 'ldapconf'
    server = models.CharField(max_length=64) # server地址
    base_dn = models.CharField(max_length=64) # Base DN值
    domainname = models.CharField(max_length=64) # 域名
    loginname = models.CharField(max_length=32) # 登录名
    username = models.CharField(max_length=32) # 用户名
    password = models.CharField(max_length=32) # 密码
    
    def __str__(self):
        return self.server

# 获取LDAP配置对象
def get_ldapconf():
    ldapconfs = LDAPConf.objects.all()
    if ldapconfs:
        ldapconf = ldapconfs[0]
        return ldapconf
    else:
        return None
        
        
# 添加用户时认证LDAP中是否有该用户名
def validate_ldap(validateusername):
    ldapconf = get_ldapconf()
    if ldapconf == None:
        return False
    username = ldapconf.username
    password = ldapconf.password
    flag = False
    try:
        Server = ldapconf.server
        baseDN = ldapconf.base_dn
        searchScope = ldap.SCOPE_SUBTREE
        searchFilter = ldapconf.loginname + "=" + validateusername
        username = ldapconf.domainname + "\\" + username
        retrieveAttributes = None
        conn = ldap.initialize(Server)
        conn.set_option(ldap.OPT_REFERRALS, 0)
        conn.protocol_version = ldap.VERSION3
        conn.simple_bind_s(username, password)
        ldap_result_id = conn.search(baseDN, searchScope, searchFilter, retrieveAttributes)
        result_set = []
        while 1:
            result_type, result_data = conn.result(ldap_result_id, 0)
            if(result_data == []):
                break
            else:
                if result_type == ldap.RES_SEARCH_ENTRY:
                    result_set.append(result_data)
                    Name,Attrs = result_data[0]
                    if hasattr(Attrs, 'has_key') and Attrs.has_key('mail'):
                        pass
                        #print Attrs['mail'][0]
                    if hasattr(Attrs, 'has_key') and Attrs.has_key('sAMAccountName'):
                        pass
                        #print Attrs['sAMAccountName'][0]
                    flag = True  
        
    except ldap.LDAPError, e:
        flag = False
    return flag
    
# LDAP登录认证
def login_ldap(username, password):
    ldapconf = get_ldapconf()
    if ldapconf == None:
        return False
    flag = False
    try:
        Server = ldapconf.server
        username = ldapconf.domainname + "\\" + username
        conn = ldap.initialize(Server)
        conn.set_option(ldap.OPT_REFERRALS, 0)
        conn.protocol_version = ldap.VERSION3
        conn.simple_bind_s(username, password)
        flag = True
    except ldap.LDAPError, e:
        flag = False
    return flag    
        
# 查询用户信息
# ***注意*** 要求keyword 是utf-8
def search_user(keyword, exactSearch=False):
    #1. 处理参数
    ldapconf = get_ldapconf()
    username = ldapconf.domainname + '\\' + ldapconf.username 
    password = ldapconf.password
    baseDN = 'OU=高德集团,DC=autonavi,DC=com'
    
    searchFilter = None
    if exactSearch:
        # 只能是用户
        searchFilter = '(&(objectClass=user)(|(CN=%s)(sAMAccountName=%s)))' % (keyword, keyword)
    else:
        searchFilter = '(&(objectClass=user)(|(CN=%s*)(sAMAccountName=%s*)))' % (keyword, keyword)
        
    retrieveAttributes = ['cn', 'sAMAccountName', 'department', 'mail', 'telephoneNumber']
    
    #2. 连接ldap服务器
    conn = ldap.initialize(ldapconf.server)
    conn.set_option(ldap.OPT_REFERRALS, 0)
    conn.protocol_version = ldap.VERSION3
    conn.simple_bind_s(username, password)
    
    item_list = None
    try:
        item_list = conn.search_st(baseDN, ldap.SCOPE_SUBTREE, searchFilter, retrieveAttributes, timeout=1)
    except BaseException,e:
        print e
        return  None
        
    
    res_list = []
    for item in item_list:
        temp = {}
        
        if 'cn' in item[1]:
            temp['cn'] = item[1]['cn'][0]
        else:
            temp['cn'] = ''
            
        if 'sAMAccountName' in item[1]:
            temp['sAMAccountName'] = item[1]['sAMAccountName'][0]
        else:
            temp['sAMAccountName'] = ''
            
        if 'department' in item[1]:
            temp['department'] = item[1]['department'][0]
        else:
            temp['department'] = ''
            
            
        if 'mail' in item[1]:
            temp['mail'] = item[1]['mail'][0]
        else:
            temp['mail'] = ''
        
        if 'telephoneNumber' in item[1]:
            phone = item[1]['telephoneNumber'][0]
            # LDAP 中的电话号码，形式为 +84107146,需要去除加号
            if phone[0]=='+':
                phone = phone[1:]
            temp['phone'] = phone
        else:        
            temp['phone'] = ''
            
        res_list.append(temp)
    return res_list
    

    
    
