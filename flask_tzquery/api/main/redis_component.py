# -*- coding:utf8 -*-

from redis import Redis
from collections import OrderedDict
from datetime import datetime
import os, re, time, xlrd

redis = Redis(host='127.0.0.1',port=6379)


def transKeyWords(keywords):
    pattern = re.compile(r"([\[\?\]\.\*\-\!\{\}])")
    keywords = sorted(keywords, key=lambda i:len(i), reverse=True)  #通过把字符串长度进行排序，缩短查询时间
    keyword = pattern.sub(r"\\"+r"\1", keywords[0])
    return keyword

def query(area, keywords):
    keyword = transKeyWords(keywords)
    colNameDict = getColNameDict()
    global redis
    rowDict = {}
    tableOrderedDict = OrderedDict()

    for key in redis.sscan_iter('rowSet',match=area.encode("utf8")+"[0-9][0-9][0-9][0-9]%%&&%%*%s*" % keyword, count=10000):
    #020304 六位，02表示专业，03表示该专业的第三个工作簿， 04表示该工作簿的第四个sheet
        flag = True
        tabIndex = key.split("%&&%")[0]
        rowContent = key.split("%&&%")[1]
        for keyword in keywords[1:]:    #To Do 要分割出来再判断，加了*再后面加%%&&%%，增了差不多一倍的时间。。查询时过滤这个关键词吧。
            if rowContent.find(keyword)==-1:
                flag = False
                break
        if flag:
            for i in range(len(keywords)):  #不使用前端的正则替换，很容易出错。后端把字符替换完即可。
                rowContent = rowContent.replace(keywords[i],"".join(['<span class="keyword',str(i),'">',keywords[i],'</span>']))
            rowDict.setdefault(tabIndex, []).append(rowContent.split("@$$@"))
        # ToDo 不能用：区分，因为单元各种会有这种符号
    # rowOrderedDict = OrderedDict(sorted(rowDict.items(),cmp=lambda a,b:int(a[0][1:])-int(b[0][1:]) if a[0][0]==b[0][0] else int(a[0][0])-int(b[0][0]), key=lambda d:int(d[0])))   #使用OrderedDict解决显示输出表格排序的问题

    rowOrderedDict = OrderedDict(sorted(rowDict.items(),cmp=lambda a,b:int(a[0][2:])-int(b[0][2:]) if a[0][0:2]==b[0][0:2] else int(a[0][0:2])-int(b[0][0:2])))   #使用OrderedDict解决显示输出表格排序的问题
    
    for k, v in rowOrderedDict.items():

        # row = OrderedDict(zip(colNameDict[k][0], v))
        # 列名一样的话，使用zip会自动删除一列！注意,使用dict会打乱顺序，使用OrderDict解决
        tableOrderedDict.setdefault(colNameDict[k][1]+" ---> "+colNameDict[k][2], {"colName":colNameDict[k][0],"rowData":v,"tabIndex":k})
        # 如何排序，按键值

    return tableOrderedDict

def getTableHash():
    tableHash = redis.hgetall("tableHash")
    return tableHash

def getFileNameDict():
    tableHash = getTableHash()
    fileDict = {}
    for k, v in tableHash.items():
        wbInfoList          = v.split("%&&%")[0].split("||")
        wbName              = wbInfoList[0]
        updateTime          = wbInfoList[1]
        lastModified        = wbInfoList[2]
        size                = wbInfoList[3]
        fileDict.setdefault(k[:4], {
            "wbName":wbName,
            "updateTime":updateTime,
            "lastModified":lastModified,
            "size":size
        })
    return fileDict

def getColNameDict():
    tableHash = getTableHash()
    colNameDict = {}
    for k, v in tableHash.items():
        tableDetailList = v.split("%&&%")
        wbName = tableDetailList[0].split("||")[0]
        sheetName = tableDetailList[1]
        colNameDict.setdefault(k, [tableDetailList[2].split("@$$@"), wbName, sheetName])
    return colNameDict

def importMemoryExcel(f, **kwargs):
    wb = xlrd.open_workbook(file_contents=f.getvalue())    #这里读取的是内存文件
    redisInstance.importWithPipe(wb, **kwargs)

def delWbInRedis(wbIndex):
    redisInstance.delWbInRedis(wbIndex)

class manageRedis():
    def __init__(self):
        self.redis = Redis(host='127.0.0.1',port=6379)

    def caculateMinWbIndex(self, classifyIndex):
        wbSet = set()
        for key,value in self.redis.hscan_iter("tableHash", match="%s*" % classifyIndex, count=10000):
            wbSet.add(key[2:4])
        a = set(["%02d" % i for i in range(1,100)]) - wbSet
        minWbIndex = min([int(i) for i in a])
        return "%02d" % minWbIndex   # 集合差集中的最小值

    def importWithPipe(self, wb, **kwargs):
        classified      = kwargs.get("classified")  #classified -> 01 专业
        filename        = kwargs.get("filename", "")
        updateTime      = kwargs.get("updateTime", "")
        lastModified    = kwargs.get("lastModified", "")
        size            = kwargs.get("size", "")

        start = time.time()
        minWbIndex = self.caculateMinWbIndex(classified)
        wbIndex = classified + minWbIndex    # 类别索引，工作簿索引都是utf8类型
        tableHash = {}
        count = 0
        i = 0
        with self.redis.pipeline(transaction=False) as p:
            for table in wb.sheets():
                print table.name
                i += 1
                tableIndex = wbIndex + "%02d" % i
                colStr = ""
                nrows = table.nrows
                ncols = table.ncols
                colnames = table.row_values(0)
                colStr = "@$$@".join(unicode(i) for i in colnames)
                
                premark = unicode(tableIndex)+unicode("%&&%")

                for rownum in range(1,nrows):
                    rowValue = []
                    for colnum in range(ncols):
                        try:
                            ctype = table.cell(rownum, colnum).ctype
                            value = table.cell_value(rownum, colnum)
                        except IndexError: #取值出现越限
                            print rownum,colnum
                            ctype = 0
                            value = ""
                        if ctype == 3:
                            try:
                                date = datetime(*xlrd.xldate_as_tuple(value, 0))    # 传参时多个参数
                                value = date.strftime("%Y/%m/%d")
                            except Exception:
                                pass
                        rowValue.append(unicode(value))

                    rowLinkStr = premark + "@$$@".join(rowValue)
                    p.sadd('rowSet',rowLinkStr.encode('utf8'))  # 都是通utf8导入的
                    count += 1
                # tableHash.setdefault(tableIndex, wbname+"%&&%"+table.name+"%&&%"+colStr+"")
                wbInfo = "||".join([filename, updateTime, lastModified, size])
                tableHash.setdefault(tableIndex, "%&&%".join([wbInfo, table.name, colStr]))
            p.hmset("tableHash", tableHash)
            p.execute()
        print count
        print time.time()-start
        
    def queryRedis(self, keyword):
        for key in self.redis.sscan_iter('rowSet',match="*%s*" % keyword, count=10000):
            print key
            
    def importTableHash(self):
        self.redis.hmset("tableHash",self.tableHash)
        
    def getTableHash(self):
        start = time.time()
        x = self.redis.hgetall("tableHash")
        print time.time()-start
        return x

    def flushRedis(self):
        self.redis.flushdb()

    def delWbInRedis(self, wbIndex):  #必须确保wbIndex是utf8字符串
        t1 = time.time()
        # import pdb;pdb.set_trace()
        with self.redis.pipeline(transaction=True) as p:    # 使能原子性操作，操作出错时不会删除数据导致bug
            for setfield in self.redis.sscan_iter('rowSet',match="%s*" % wbIndex, count=500000):
                p.srem("rowSet", setfield)
            for hashkey,hashvalue in self.redis.hscan_iter("tableHash", match="%s*" % wbIndex, count=10000):
                p.hdel("tableHash", hashkey)
            p.execute()
        print time.time()-t1


redisInstance = manageRedis()
