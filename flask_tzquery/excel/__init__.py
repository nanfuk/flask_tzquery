#-*-coding:utf8-*-
import win32com.client
import pdb

print "test"
xlsApp = win32com.client.DispatchEx('Excel.Application') #不用Dispatch是因为待会关闭的时候会把其它Excel表格也关闭掉。

#from handler import *