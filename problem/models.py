# -*- coding:utf-8 -*-
from django.db import models
from django.db import connection
from utils.utils import listToStr


# problem_type
class ProblemType(models.Model):
    # 重新定义表名
    class Meta:
        db_table = 'problem_type'
    # 节点名称
    text = models.CharField(max_length=64)
    # 父节点ID
    parent_id = models.IntegerField()
    # 层级
    level = models.IntegerField()
    # 是否有效 0:无效,1:有效
    # 注意：用户对问题类目的删除操作，只会导致此字段值被置为0
    is_available = models.IntegerField()
    

# 提取树形结构,并返回以node_id 为根的树形结构对应的字典
def tree_structure(node_id):
    root_node = ProblemType.objects.get(id=node_id)
    
    dd = {}
    #获取子树的根节点
    dd["id"] = root_node.id
    dd["text"] = root_node.text
    attributes = {'level':root_node.level}
        
    dd["attributes"] = attributes

    # 判断其是否由子节点
    # 注意 is_available 字段
    node_list = ProblemType.objects.filter(parent_id=node_id,is_available=1).order_by('text')
    child_list = []
    for item in node_list:
        item_struct = tree_structure(item.id)
        if item_struct:
            child_list.append(item_struct)
            
    if child_list:
        dd["state"] = "closed"   
        dd["children"] = child_list
        
    return dd
    
# 增加子节点
def append_node(parent_id,text):
    parent_node = ProblemType.objects.get(id=parent_id)
    node = ProblemType();
    node.text = text;
    node.parent_id = parent_id;
    node.level = parent_node.level + 1
    node.is_available = 1
    node.save();
            
    return node;
    

# 更新节点的显示文字
def update_node(node_id,text):
    node = ProblemType.objects.get(id=node_id)
    node.text = text
    node.save();
        
# 删除树中的节点,注意此节点可能有子节点    
def delete_node(node_id):
    # 遍历以此节点为根的子树
    id_list = []
    queue = [node_id]  
    #　广度优先遍历
    while len(queue) > 0 :
        # 访问次节点
        nid = queue.pop(0);
        id_list.append(nid);
        #判断其是否由子节点
        node_list = ProblemType.objects.filter(parent_id=nid)
        for item in node_list:
            queue.append(item.id)
    # 执行删除操作
    ids = listToStr(id_list)
    
    # 伪删除 只将有效位置成无效
    #使用基础函数访问数据库
    cursor = connection.cursor()
    sql = "update problem_type set is_available = 0 where id in (" + ids + ")"
    cursor.execute(sql)
    
# 根据第3级问题类目生成问题类目描述
def getProblemType(problem_type_third):
    # 第3级问题类目
    item_third = ProblemType.objects.get(id=problem_type_third)
    # 第2级问题类目
    item_second = ProblemType.objects.get(id=item_third.parent_id)
    # 第1级问题类目
    item_first = ProblemType.objects.get(id=item_second.parent_id)
    
    return item_first.text + '->' + item_second.text + '->' + item_third.text
    
    

    
    
    
    
    
    