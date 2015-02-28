# -*- coding:utf8 -*-
"""
调用access.Application的DoCmd.RunCommand(4)命令。测试能否压缩数据库！
"""
import win32com.client
import os
import pdb

accessFile = r"C:\base_db1.accdb"

accApp = win32com.client.Dispatch("Access.Application")
try:
    accApp.OpenCurrentDatabase(accessFile)
except Exception,e:
    print e[2][2]
#pdb.set_trace()
#accApp.DoCmd.RunCommand(4)
"""
try:
    accApp.RunCommand(4)
except Exception,e:
    print e
"""
accApp.CloseCurrentDatabase()
"""
strSource = r"C:\base_db.accdb"
strDestination = r"C:\tmp1.accdb"
if os.path.exists(strDestination):
    os.remove(strDestination)

try:
    accApp.CompactRepair(LogFile=False, SourceFile=strSource, DestinationFile=strDestination)
except Exception,e:
    print e[2][2]

os.remove(strSource)
os.rename(strDestination, strSource)
"""