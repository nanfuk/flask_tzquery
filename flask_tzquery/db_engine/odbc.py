# -*- coding:utf8 -*-
import os
import pyodbc
import json
import pdb
import collections

#db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "base_db.accdb")
#db = os.path.join(os.path.dirname(os.path.abspath(__file__)),
#                    "database","base_db.accdb")

#print db

class accessdb():
    def __init__(self):
        self.conn = pyodbc.connect("Driver={Microsoft Access Driver (*.mdb, *.accdb)};Dbq="+db,
                                autocommit=True)

    def execute(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql)

    def search_by_table_index(self, strList, area, index):
        if area == "01":
            area = u"('传输台账','波分台账')"
        elif area == "02":
            area = u"('数据台账')"
        elif area == "03":
            area = u"('波分台账')"
        elif area == "04":
            area = u"('集团客户评价表')"

        sql1 = u"select 新表名,字段连接,序号 from tables_table left join files_table on \
                tables_table.所属文件=files_table.文件名 where 分类 in %s and tables_table.序号> %d order by 序号" % (area,index)

        cur1 = self.conn.cursor()
        cur2 = self.conn.cursor()
        fields_data = [chr(x) for x in range(65,91)]
        fields_column = [('field',chr(x)) for x in range(65,91)]
        #width = [("width",150)]*26   #设置宽度用的，都设为100

        for r1 in cur1.execute(sql1):
            #if t1 == 1:   #代表已经搜索完了??怎么代表搜
            #    index = 0
            #    return
            tablename = r1[0]
            addstring = r1[1]
            index = r1[2]

            sql2 = ""
            for str in strList:
                sql2 += u" and (%s like '%%%s%%')" % (addstring, str)
            sql2 = sql2.lstrip(" and")
            sql3 = u"select * from [%s] where " % (tablename) + sql2

            t2 = cur2.execute(sql3).fetchall()
            if t2!=[]:  #就是有结果的意思
                column_titles = [('title',desc[0].decode('gbk')) for desc in cur2.description]    #这得出表的列名，因为是gbk编码的，得转为Unicode
                #column_titles是[('title','表一'), ('title','表二')....]
                #zip_out = zip(fields_column, column_titles,width) 
                zip_out = zip(fields_column, column_titles) 
                #fields_column是[('field','A'), ('field','B')....]
                #column_titles是[('title','表一'), ('title','表二')....]
                #结果是是[(('field','A'),('title','表一')), (('field','B'),('title','表二')), ....] 
                columns = []
                datas = []
                for _ in zip_out:   #_是(('field','A'),('title','表一'))
                    #_ = collections.OrderedDict(_)
                    _ = dict(_)     #_是{'field': 'A', 'title': '表一'}
                    columns.append(_)
                    #结果是[{'field': 'A', 'title': '表一'},{'field': 'B', 'title': '表二'},...]
                for r2 in t2:
                    #data = collections.OrderedDict(zip(fields, r2))
                    data = dict(zip(fields_data, r2))
                    #fields_data是["A","B",...]
                    #r2是(u'\u4e94\u534e\u6751\u5357', u'\u4e94\u534e\u6751\u5357DL',...)
                    #结果是{"A":u'\u4e94\u534e\u6751\u5357',"B":u'\u4e94\u534e\u6751\u5357DL',...}
                    datas.append(data)
                #pdb.set_trace()
                json_data = json.dumps({'columns':[columns],'datas':datas,'index':index})
                return json_data
            

            #这是easyui表格需要的列设置参数columns=[[{‘field’:'A', 'title':'表一'},{‘field’:'B', 'title':'表二'}]]
            #datas=[{'A':'data1','B':'data2',...}]
        
    def search(self, strList, area):
        if area == "01":
            area = u"('其它','波分台账')"
        elif area == "02":
            area = u"('集团客户评价表')"
        elif area == "03":
            area = u"('波分台账')"
        elif area == "04":
            area = u"('其它')"
        sql1 = u"select 新表名,字段连接 from tables_table left join files_table on \
                tables_table.所属文件=files_table.文件名 where 分类 in %s order by 序号" % area

        cur1 = self.conn.cursor()
        cur2 = self.conn.cursor()
        
        for t1 in cur1.execute(sql1):
            tablename = t1[0]
            addstring = t1[1]
            sql2 = ""
            for str in strList:
                sql2 += u" and (%s like '%%%s%%')" % (addstring, str)
            sql2 = sql2.lstrip(" and")
            sql3 = u"select * from [%s] where " % (tablename) + sql2
            
            
            try:
                cur2.execute(sql3)
                columns = [desc[0].decode('gbk') for desc in cur2.description] #列名列表
                yield cur2.fetchall(), columns, tablename    #返回的是[("值11","值12","值13"),("值21","值22","值23")]
            except:
                pdb.set_trace()
                pass
        
        """
        while not rs1.EOF:
            tablename = rs1.Fields.Item(u'新表名').Value
            addstring = rs1.Fields.Item(u'字段连接').Value
            sql2 = ""
            for str in strList:
                sql2 += ' and (%s like "%%%s%%")' % (addstring, str)
            sql2 = sql2.lstrip(" and")
            sql3 = u'select * from [%s] where ' % (tablename) + sql2
            #sql2 = u'select * from [%s] where (%s like "%%%s%%") and (%s like "%%太阳城%%")' % (tablename, addstring, str, addstring)
            #pdb.set_trace()
            rs2 = oledb.RsExecute(self.conn, sql3)
            
            if rs2.EOF==False:
                yield rs2, tablename
            rs1.MoveNext()
            select * from [3G基站电路台帐(最新)__WLAN电路] where ([F7]+[电路名称(旧)]+[调度单号]+[接入环号]+[路由]+[配置人] like '*新时空*')
        """

    def get_client_json(self):
        sql = "select * from client_names"
        cur = self.conn.cursor()
        fields_data = ["itemid","client-name","customer-manager"]
        datas = []

        for row in cur.execute(sql):
            data = dict(zip(fields_data, row))
            #fields_data是["A","B",...]
            #r2是(u'\u4e94\u534e\u6751\u5357', u'\u4e94\u534e\u6751\u5357DL',...)
            #结果是{"A":u'\u4e94\u534e\u6751\u5357',"B":u'\u4e94\u534e\u6751\u5357DL',...}
            datas.append(data)
        #pdb.set_trace()
        json_data = json.dumps(datas)
        return json_data

    def close(self):
        self.conn.close()