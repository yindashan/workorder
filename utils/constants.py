# -*- coding:utf-8 -*-

# 日志级别字典
log_level_dict = {0:'DEBUG', 1:'INFO', 2:'WARN', 3:'ERROR'}

# 权限类型
permission_type_dict = {1:u'系统管理', 2:u'配置管理', 3:u'工作台', 4:u'区域工单管理', 5:u'字段展现', 6:u'其他'}

# 日志类型
log_type_dict = {0:u'其他日志', 1:u'用户管理日志', 2:u'角色管理日志'}

# 监控类型
alarm_type_dict = {0:u'否', 1:u'是'}

# yes_no
yes_no_dict = {0:u'否', 1:u'是'}

# 优先级
priority_dict = {1:u'紧急', 2:u'普通'}

# 权重
weight_dict = {1:'1', 2:'2', 3:'3', 4:'4', 5:'5', \
               6:'6', 7:'7', 8:'8', 9:'9', 10:'10' }
               
# 工单状态
# 由于工单一创建就被分配了，事实上不会出现未接受的情况
order_status_dict = {1:u'未接受', 2:u'已接受', 3:u'已解决', 4:u'已升级', 5:u'已评价', 6:u'已取消'}

# 工单流转记录动作
wander_action_dict = {1:u'创建&分配', 2:u'升级', 3:u'已解决&待评级', 4:u'评级完成&关闭', 5:u'工单被取消'}

# 工单从创建到解决耗时
consume_time_dict = {1:u'<30分钟', 2:u'<1小时', 3:u'<2小时', 4:u'<1天', 5:u'>1天'}

# 来源
source_dict = {1:u'电话', 2:u'网络'}

# 满意度(反馈评级)
feedback_rate_dict = {1:u'非常不满意', 2:u'不满意', 3:u'满意', 4:u'比较满意', 5:u'非常满意'}

# 反馈表状态
feedback_status_dict = {0:u'提交', 1:u'已回复', 2:u'已关闭'}

# 无线密码账户状态
wireless_status_dict = {0:u'未启用', 1:u'正常', 2:u'失效', 3:u'停用'}

# IT任务状态
ittask_status_dict = {0:u'进行中',1:'关闭'}

# 更新频率
update_period_dict = {1:'1天', 3:'3天', 7:'1周', 14:'2周'}

# IT人员工单状态
staff_status_dict = {0:'空闲中', 1:'忙碌中，请等待', 2:'非常忙碌，请耐心等待', 3:'暂时无法接收更多工单'}






