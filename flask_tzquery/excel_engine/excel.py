 #-*- coding:utf8 -*-

import win32com.client
import pdb
import pythoncom

def init():
    #pythoncom.CoInitialize()
    instance = excel()
    return instance


class excel():
    def __init__(self):
        pythoncom.CoInitialize()
        self.xlsApp = win32com.client.Dispatch('Excel.Application') #不用Dispatch是因为待会关闭的时候会把其它Excel表格也关闭掉。

        
    def open(self, excelName, sheet, isDisplay):   #打开excel文件，并返回是否为只读。
        self.xlsBook = self.xlsApp.Workbooks.Open(excelName)
        self.xlsSheet = self.xlsBook.Sheets(sheet)  #应该写成(1), 不应该写成[1].有些电脑会出错,不知原因.
        
        if isDisplay:
            self.xlsApp.WindowState = 3   #最小化窗口,1为默认,2为最小，3为最大
            self.xlsApp.Visible = 1  #窗口可视
        else:
            self.xlsApp.Visible = 0
        if self.xlsBook.ReadOnly == True :
            return None
        else:       
            return self.xlsBook

    def addtemplate(self, template_path, sheet, isDisplay):
        self.xlsBook = self.xlsApp.Workbooks.Add(template_path)
        self.xlsSheet = self.xlsBook.Sheets(sheet)
        if isDisplay:
            self.xlsApp.WindowState = 3   #最小化窗口,1为默认,2为最小，3为最大
            self.xlsApp.Visible = 1  #窗口可视
        else:
            self.xlsApp.Visible = 0
        return None

    def addnew(self, sheet, isDisplay): #新建工作簿
        self.xlsBook = self.xlsApp.Workbooks.Add()
        self.xlsSheet = self.xlsBook.Sheets(sheet)
        if isDisplay:
            self.xlsApp.WindowState = 3   #控制窗口显示大小,1为默认,2为最小，3为最大
            self.xlsApp.Visible = 1  #窗口可视
        else:
            self.xlsApp.Visible = 0
        return None

    def write(self, row, column, value):
        self.xlsSheet.Cells(row, column).Value = value
        #print u"写入%s成功" % value
        
    def write_line(self, row, column,valueset):
        for i in range(len(valueset)):
            self.write(row, column+i, valueset[i])

    def read(self, row, column):
        return self.xlsSheet.Cells(row, column).Value   #这就实现了读取单元格数据

    def setInteriorColor(self, row, column, colorIndex, settimes=None):    #settimes表示改行连续多少格设这种颜色,colorIndex中6表示黄，3表示红，5表示深蓝，8表示淡蓝
        if settimes:
            for i in range(settimes):
                self.xlsSheet.Cells(row, column+i).Interior.ColorIndex=colorIndex
        else:
            self.xlsSheet.Cells(row, column).Interior.ColorIndex=colorIndex
        

  #*************************得出从第几行开始写入. *************************
    def getRow(self):
        i = 1
        while self.xlsSheet.Cells(i,1).Value:
            i += 1

        #pdb.set_trace()
        return i

    def close(self, isSave):    #参数为是否保存
        #pdb.set_trace()
        if isSave and not self.xlsBook.ReadOnly:
        #if self.xlsBook.ReadOnly == True:
            self.xlsBook.Close(True)
        else:
            #self.xlsApp.WindowState = 3
            #pdb.set_trace()
            self.xlsBook.Close(False)
        #self.xlsApp.Quit()
        
        #self.xlsApp.WindowState = 3
        #pdb.set_trace()
        #self.xlsBook.Close(True)
        #self.xlsApp.Quit()
        