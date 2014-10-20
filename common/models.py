# -*- coding:utf-8 -*-
class BusinessException(BaseException):
    def __init__(self,code):
        #　错误码值
        self.code = code 
    
    def __str__(self):
        return 'ErrorCode:' + str(self.code)

