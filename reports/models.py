# -*- coding:utf-8 -*-
from django.db import connection
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from django.template import Context, Template
from utils.constants import source_dict, feedback_rate_dict, consume_time_dict
from order.models import Order 
from area.models import Area

# 饼图关键信息
class PieChart(object):
    def __init__(self):
        # 标题
        self.title = ''
        # label信息,以逗号分割
        self.keys_desc = ''
        # 值，以逗号分割
        self.keys_data = ''
        

# 工单来源比例饼图
def order_source_pie(start_time, end_time):
    key_list = []
    value_list = []
    for item in source_dict:
        key_list.append(source_dict[item])
        value = Order.objects.filter(source=item, create_time__gte=start_time,
            create_time__lt=end_time).count()
        
        value_list.append(str(value))
        
    p = PieChart() 
    p.title = '工单按来源统计'
    p.keys_desc = ','.join(key_list)
    p.keys_data = ','.join(value_list)
    return p
    
# 办公区域比例饼图
def order_area_pie(start_time, end_time):
    key_list = []
    value_list = []
    area_list = Area.objects.all()
    for item in area_list:
        key_list.append(item.name)
        value = Order.objects.filter(area_id=item.id, create_time__gte=start_time,
            create_time__lt=end_time).count()
        
        value_list.append(str(value))
        
    p = PieChart() 
    p.title = '工单按办公区域统计'
    p.keys_desc = ','.join(key_list)
    p.keys_data = ','.join(value_list)
    return p

# 反馈比例饼图
def order_feedback_pie(start_time, end_time):
    key_list = []
    value_list = []
    for item in feedback_rate_dict:
        key_list.append(feedback_rate_dict[item])
        value = Order.objects.filter(feedback_rate=item, create_time__gte=start_time,
            create_time__lt=end_time).count()
        
        value_list.append(str(value))
        
    p = PieChart() 
    p.title = '工单按反馈评价统计'
    p.keys_desc = ','.join(key_list)
    p.keys_data = ','.join(value_list)
    return p

# 处理时间比例饼图
def order_spendtime_pie(start_time, end_time):
    cursor = connection.cursor()
    key_list = []
    value_list = []
    #consume_time_dict = {1:u'<30分钟', 2:u'<1小时', 3:u'<２小时', 4:u'<1天', 5:u'>1天'}
    append_str = " and create_time >= %s and create_time < %s"
    pre_value = 0
    # 1. 30分钟以内
    sql = "select sum(timediff(close_time, create_time) < '00:30:00') from work_order where status in (3,5,6)"
    cursor.execute(sql + append_str, (start_time, end_time))
    value = cursor.fetchone()[0]
    if value is None:
        value = 0
    key_list.append('<30分钟')
    value_list.append(str(value - pre_value))
    pre_value = value
     
    # 2. 30分钟　到 1小时
    sql = "select sum(timediff(close_time, create_time) < '01:00:00') from work_order where status in (3,5,6)"
    cursor.execute(sql + append_str, (start_time, end_time))
    value = cursor.fetchone()[0]
    if value is None:
        value = 0
    key_list.append('<1小时')
    value_list.append(str(value - pre_value))
    pre_value = value
    
    # 3. 1小时 到 2小时
    sql = "select sum(timediff(close_time, create_time) < '02:00:00') from work_order where status in (3,5,6)"
    cursor.execute(sql + append_str, (start_time, end_time))
    value = cursor.fetchone()[0]
    if value is None:
        value = 0
    key_list.append('<2小时')
    value_list.append(str(value - pre_value))
    pre_value = value
    
    # 4. 2小时　到　1天
    sql = "select sum(timediff(close_time, create_time) < '24:00:00') from work_order where status in (3,5,6)"
    cursor.execute(sql + append_str, (start_time, end_time))
    value = cursor.fetchone()[0]
    if value is None:
        value = 0
    key_list.append('<1天')
    value_list.append(str(value - pre_value))
    pre_value = value
    
    # 5. 大于1天
    sql = "select count(1) from work_order where status in (3,5,6)"
    cursor.execute(sql + append_str, (start_time, end_time))
    value = cursor.fetchone()[0] 
    if value is None:
        value = 0
    key_list.append('>1天')
    value_list.append(str(value - pre_value))
    pre_value = value
    
        
    p = PieChart() 
    p.title = '工单按处理时间统计'
    p.keys_desc = ','.join(key_list)
    p.keys_data = ','.join(value_list)
    return p
    
    
def pie_info(start_time, end_time):
    pie_list = []
    pie_list.append(order_source_pie(start_time, end_time))
    pie_list.append(order_area_pie(start_time, end_time))
    pie_list.append(order_feedback_pie(start_time, end_time))
    pie_list.append(order_spendtime_pie(start_time, end_time))
    return pie_list
    
    
    
    