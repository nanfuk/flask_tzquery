#-*- coding:utf8 -*-
#import win32com.client
import pythoncom
from . import xlsApp

#pythoncom.CoInitialize()    #因为是从__init__调用这个函数的，所以得加这一句
print xlsApp

def open(excelName, sheet, isDisplay):
    xlsBook = xlsApp.Workbooks.Open(excelName)
    xlsSheet = xlsBook.Sheets(sheet)
    if isDisplay:
            xlsApp.WindowState = 3   #最小化窗口,1为默认,2为最小，3为最大
            xlsApp.Visible = 1  #窗口可视
    else:
        xlsApp.Visible = 0
    if xlsBook.ReadOnly == True :
        return True
    else:
        return handler(xlsBook, xlsSheet)

def close(instance):
    instance.close()
    xlsApp.Quit()


class handler():
    def __init__(self, xlsBook, xlsSheet):
        self.xlsBook = xlsBook
        self.xlsSheet = xlsSheet

    def addtemplate(self, template_path, sheet, isDisplay):
        self.xlsBook = self.xlsApp.Workbooks.Add(template_path)
        self.xlsSheet = self.xlsBook.Sheets(sheet)
        if isDisplay:
            self.xlsApp.WindowState = 3   #最小化窗口,1为默认,2为最小，3为最大
            self.xlsApp.Visible = 1  #窗口可视
        else:
            self.xlsApp.Visible = 0
        return None

    def addnew(self, sheet, isDisplay):
        self.xlsBook = self.xlsApp.Workbooks.Add()
        self.xlsSheet = self.xlsBook.Sheets(sheet)
        if isDisplay:
            self.xlsApp.WindowState = 3   #最小化窗口,1为默认,2为最小，3为最大
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

    def close(self):
        #pdb.set_trace()
        
        if self.xlsBook.ReadOnly == True:
            self.xlsBook.Close(False)
        else:
            #self.xlsApp.WindowState = 3
            #pdb.set_trace()
            self.xlsBook.Close(True)