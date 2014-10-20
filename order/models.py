# -*- coding:utf-8 -*-
from django.db import models

# our own code
import time
import random
from staff.models import Staff
from operator import itemgetter
from problem.models import getProblemType
from utils.constants import order_status_dict,feedback_rate_dict,source_dict,consume_time_dict
from executive.models import Executive
from area.models import Area


# 工单
class Order(models.Model):
    # 重新定义表名
    class Meta:
        db_table = 'work_order'
    # 主键由Django生成
    # 创建时间
    create_time = models.DateTimeField()
    # 解决时间
    close_time = models.DateTimeField(null=True)
    # 来源    1: '电话', 2:'网络'
    source = models.IntegerField()
    # 创建人账户名
    creator = models.CharField(max_length=32)
    # 用户姓名（故障申报人) 中文
    realname = models.CharField(max_length=64)
    # 账户名（故障申报人) 
    accountname = models.CharField(max_length=32)
    # 部门
    department = models.CharField(max_length=128)
    # 电子邮件
    email = models.CharField(max_length=64)
    # 电话
    phone = models.CharField(max_length=32)
    # 故障类目(三级)
    problem_type_third = models.IntegerField()
    # 故障描述
    problem_desc = models.TextField()
    # 优先级 1:优先 2:普通
    priority_level = models.IntegerField()
    # 评价　0~5 分
    feedback_rate = models.IntegerField()
    # 评价备注
    feedback_comment = models.TextField(null=True)
    # 处理人的用户名
    dealer_realname = models.CharField(max_length=64)
    # 处理人的账户名称
    dealer_accountname = models.CharField(max_length=32)
    # 1:u'未接受', 2:u'已接受', 3:u'已解决', 4:u'已升级', 5:u'已评价', 6:u'已取消'
    status = models.IntegerField()
    # 工单编号 
    case_number = models.CharField(max_length=32)
    # 工位
    workseat = models.CharField(max_length=64)
    
    # 所属区域
    area = models.ForeignKey(Area) # 多对一关联

# 压缩工单编号
# 20140117103043038904 -> 201***8904
def compress_number(num_str):
    if len(num_str) > 10:
        return num_str[0:3] + '***' + num_str[-4:]
    return num_str
    

# 工单扩展类,用于工单列表展示
class OrderExtend():
    def __init__(self, obj, request):
        self.id = obj.id
        self.case_number = compress_number(obj.case_number)
        self.create_time = obj.create_time.strftime('%Y-%m-%d %H:%M')
        # 故障类目(第三级)
        self.problem_type = getProblemType(obj.problem_type_third)
        # 故障申报人
        self.realname = obj.realname
        # 处理人
        self.dealer_realname = obj.dealer_realname
        # 区域id
        self.area = obj.area.name
        # 工单状态
        self.status = order_status_dict[obj.status]
        # 工单状态id
        self.status_id = obj.status
        # 工单可处理
        if obj.status in [2,4] and "deal_order" in request.session["authority_set"]:
            self.can_deal = True
        else:
            self.can_deal = False
        # 工单可评价
        if obj.status==3 and (request.user.username == obj.creator or  \
            "order_feedback" in request.session["authority_set"]):
            self.can_appraise = True
        else:
            self.can_appraise = False
        
        # 工单优先级
        self.priority_level = obj.priority_level
        
        # 创建到已解决耗时类型    1:'30分钟以内', 2:'1小时以内', 3:'２小时以内', 4:'1天以内', 5:'超过1天'
        if obj.status == 3 or obj.status == 5:
            self.consume_time_type = consume_time_dict[check_consume_time(obj.close_time - obj.create_time)]
        # 来源
        self.source = source_dict[obj.source]
        
        # 问题描述
        self.problem_desc = obj.problem_desc
        
        #　满意度
        if obj.status == 5:
            self.feedback_rate = feedback_rate_dict[obj.feedback_rate]

# 耗时类型
# 1:'30分钟以内', 2:'1小时以内', 3:'２小时以内', 4:'1天以内', 5:'超过1天'     
def check_consume_time(d):
    # 分钟  
    ll = [30, 60, 120, 1440]
    consume_time_type = 5
    num = d.days*24*60 + d.seconds/60
    for i in range(len(ll)):
        if num < ll[i]:
            consume_time_type = i + 1
            break;
    return consume_time_type
        
# 工单备注
class Remark(models.Model):
    # 重新定义表名
    class Meta:
        db_table = 'work_order_remark'
    # 主键由Django生成
    # 创建时间
    create_time = models.DateTimeField()
    # IT工程师账户名称
    accountname = models.CharField(max_length=32)
    # IT工程师姓名
    realname = models.CharField(max_length=32)
    # 备注
    comment = models.TextField()

    # 工单 
    order = models.ForeignKey(Order) # 多对一关联
    
# 流转表
class Wander(models.Model):
    # 重新定义表名
    class Meta:
        db_table = 'wander_record'
    # 创建时间(流转发生时间)
    create_time = models.DateTimeField()
    # 来源(中文姓名)
    source_name = models.CharField(max_length=32)
    # 目标(中文姓名)
    target_name = models.CharField(max_length=32)
    # 动作
    operation = models.IntegerField()
    
    # 工单
    order = models.ForeignKey(Order) # 多对一关联
    
# 产生工单编号(共20个字符)
# 工单号产生规则,由两部分组成　
# 1.时间14个字符 时间 2013-07-31 17:00:18 转换成 20130731170018
# 2.随机数　6个字符   
def genCaseID():
    str1 = time.strftime('%Y%m%d%H%M%S',time.localtime())
    str2 = str(random.randint(0,1000000 -1))
    # 长度如果不足，则补足
    temp = '0000000'
    str2 = temp[0:6-len(str2)] + str2
    return str1 + str2
    
# 系统指派一个合适的IT工程师
# 计算方法
# 1) 根据权重计算出，该区域中每个工程师接受到的工单应达到的占比(目标)
# 2) 计算从当天00:00 开始,该区域中每个工程师接收到的工单的实际占比(现状)
# 3) 做差，选出相差最大的工程师
# ***注意***  小心工单数为0的情况
def designate_engineer(area_id):
    start_time = time.strftime('%Y-%m-%d',time.localtime())
    count = Order.objects.filter(area_id=area_id,create_time__gte=start_time).count()
    if count == 0:
        count = 1
        
    staff_list = Staff.objects.filter(area_id=area_id,is_available=1)
    
    # 特殊情况此区域没有工程师
    if not staff_list:
        return None
    
    # 1) 理论百分比(目标)
    weight_count = 0
    theory_percent_list = []
    for staff in staff_list:
        weight_count += staff.weight
        
    for staff in staff_list:
        theory_percent_list.append(float(staff.weight)/weight_count)
    
    # 2) 实际百分比
    real_percent_list = []
    for staff in staff_list:
        get_count = Order.objects.filter(area_id=area_id,create_time__gte=start_time, \
                    dealer_accountname=staff.accountname).count()
        real_percent_list.append(float(get_count)/count)
        
    # 3)　做差,排序
    ll = []
    for i in range(len(theory_percent_list)):
        item = (theory_percent_list[i] - real_percent_list[i], staff_list[i])
        ll.append(item)
        
    ll=sorted(ll, key=itemgetter(0),reverse=True)
    
    return ll[0][1]
    
# 如果提交人或故障申报人在高管名单中，且此高管对应的IT工程师，有合适的候选人(有效)
# 则返回此IT工程师，否则返回None
def executive_helper(order):
    executive_list = Executive.objects.all()
    se_list = [item.accountname for item in executive_list]
    se = None
    # 提交人
    if order.creator in se_list:
        se = order.creator
    # 申报人
    elif order.accountname in se_list:
        se = order.accountname
    
    # 确实跟高管有关
    if se:
        executive = Executive.objects.get(accountname=se)
        # 查看一下，高管的指定工程师是否可用
        staff = Staff.objects.get(id=executive.first_engineer_id)
        if staff.is_available:
            return staff
            
        staff = Staff.objects.get(id=executive.second_engineer_id)
        if staff.is_available:
            return staff
            
    return None
        
    

