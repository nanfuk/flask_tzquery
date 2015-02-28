# -*- coding:utf8 -*-
import os
#os.system("dir")
import subprocess
import shutil

#filePath = r"\\10.117.193.234\资源调度\传输\SDH客户路由台账\客户电路1(融合资源).xlsx".decode('utf8')
filePath = r"C:\传输值班台账汇总1\3G基站电路台帐(最新).xlsm".decode("utf8")
excelDir = r"C:\传输值班台账汇总".decode('utf8')
try:
    shutil.copy(filePath, excelDir)
except Exception,e:
    print e