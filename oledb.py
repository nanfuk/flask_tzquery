# -*- coding:utf8 -*-
"""
利用Excel文件获得表名与列名，新建数据库，并生成两个表。t1（表名，新表名，文件名，字段连接）、t2（列名，表名，类型，是否查询）。
"""
#TODO:

import win32com.client
import os
import time
import re
import json
import pythoncom
import pdb
from os.path import splitext

class oledb():
    adSchemaTables = 20
    adSchemaColumns = 4
    adCmdText = 1

    acImport =  0     #表示导入数据
    acSpreadsheetTypeExcel9 = 8       #Microsoft Excel 2000 格式
    
    def __init__(self):
        
        pass

    @classmethod
    def init_conn(self):
        print u'正在初始化'
        self.file_path = r'C:\传输值班台账汇总'.decode('utf8')
        self.db_path = r'C:\Users\John\Desktop\execel与access\base_db.accdb'.decode('utf8')
        self.access_path = r'C:\Users\John\Desktop\execel与access\base_db.accdb'.decode('utf8')
        self.pattern = re.compile(r'.*[\$|\$\']$')   #正则表示匹配以$及$'结尾的字符串,初步优化得到的excel表名
        #self.file1 = open(r'C:\Users\John\Desktop\execel与access\debug.txt'.decode('utf8'), 'w')
        
    @classmethod
    def connect_accessdb(self, db_path):
        DSN = r'PROVIDER=Microsoft.Ace.OLEDB.12.0;DATA SOURCE=%s;' % db_path
        self.conn_accessdb = win32com.client.Dispatch(r'ADODB.Connection')
        self.comm_accessdb = win32com.client.Dispatch(r'ADODB.Command')
        self.conn_accessdb.Open(DSN)
        self.comm_accessdb.ActiveConnection = self.conn_accessdb
        self.comm_accessdb.CommandType = self.adCmdText
    
    @classmethod
    def connect_excel(self, excel_path):
        DSN = r"PROVIDER=Microsoft.Ace.OLEDB.12.0;DATA SOURCE=%s;Extended Properties='Excel 12.0;HDR=YES;IMEX=1'" % excel_path
        #Excel2007必须使用Microsoft.Ace.OLEDB.12.0;#HDR表示首行作为列名
        #IMEX=1 时为“汇入模式”，这个模式开启的 Excel 档案只能用来做“读取”用途
        self.conn_excel = win32com.client.Dispatch(r'ADODB.Connection')
        self.comm_excel = win32com.client.Dispatch(r'ADODB.Command') 
        try:
            self.conn_excel.Open(DSN)
        except Exception,e:
            print e[2][2]
        self.comm_excel.ActiveConnection = self.conn_excel
        self.comm_excel.CommandType = self.adCmdText  

    @classmethod
    def connect_accessapp(self, access_path):
        self.accessApplication = win32com.client.Dispatch('Access.Application')
        try:
            
            self.accessApplication.OpenCurrentDatabase(access_path) #一定得连接数据库,而且这个access_path必须得是绝对路径！
        except Exception,e:
            print e[2][2]

    @classmethod    
    def execute_sql(self, comm, sql):
        #print u'执行SQL命令:%s' % sql
        comm.CommandText = sql
        #pdb.set_trace()
        try:           
            rs = comm.Execute()

        except Exception,e:
            print u'执行SQL命令:%s 出错：' % sql
            try:
                print e[2][2]
            except:
                print e
            return None
        if isinstance(rs, tuple):    #判断是否是tuple类型
            return rs[0]
        else:
            return None

    @classmethod
    def del_all_tables(self):        #删除t1,t2管理表
        a = self.conn_accessdb.OpenSchema(self.adSchemaTables)
        while not a.EOF:
            if str(a("TABLE_TYPE"))=="TABLE":
                tableName = str(a("TABLE_NAME")).decode('utf8')
                sql = u"drop table [%s];" % tableName
                print u'正在删除[%s]表' % tableName
                self.execute_sql(self.comm_accessdb, sql)
            a.MoveNext()
        """
        sql = u"drop table [t1];"
        self.execute_sql(self.comm_accessdb, sql)
        sql = u"drop table [t2];"
        self.execute_sql(self.comm_accessdb, sql)
        """
    @classmethod
    def create_manage_table(self):    #创建t1,t2管理表
        print u'正在创建新表'
        #self.connect_accessdb(self.db_path)
        sql = u"create table tables_table (序号 int identity(1,1), 旧表名 varchar(100), 新表名 varchar(200), 所属文件 varchar(150), 字段连接 text);"
        self.execute_sql(self.comm_accessdb, sql)
        sql = u"create table fields_table (序号 int identity(1,1), 列名 varchar(100), 类型 int, 是否查询 bit, 所属表 varchar(100));"
        self.execute_sql(self.comm_accessdb, sql)

    @classmethod
    def write_tables_table(self):
        for filename in os.listdir(self.file_path):
            pathname = os.path.join(self.file_path, filename)
            self.connect_excel(pathname)
            print u'\n正在获取%s的表名。' % filename
            a = self.conn_excel.OpenSchema(self.adSchemaTables)
            #20代表adSchemaTables
             
            while not a.EOF:
                if str(a("TABLE_TYPE"))=="TABLE":
                    #必须加str()进行类型转换，原本是<'type' instance>
                    #有"TABLE" "SYSTEM TABLE" "ACCESS TABLE"三种类型
                    tableName = str(a("TABLE_NAME")).decode('utf8')
                    filename = splitext(filename)[0]
                    

                    match = self.pattern.search(tableName)
                    if match:   #如果匹配到，则match不为None
                        newtableName = filename+"___"+tableName.strip("'$")
                        sql = u'insert into tables_table(旧表名, 新表名, 所属文件) values("%s", "%s", "%s")'% (tableName, newtableName, filename)#这里使用双引号，是为了防止值带单引号时出错。
                        self.execute_sql(self.comm_accessdb, sql)

                        #self.write_fields_table(self, tableName, newtableName)  #填充fields_table，步骤错误，这样导入的话会把F27~F255的列都导入
                        """待添加:填充tables_table的连接字段，参考step5"""
                a.MoveNext()
            a.Close()
            self.conn_excel.Close()

    @staticmethod
    def write_fields_table(self, table_name, newtableName):
        a = self.conn_excel.OpenSchema(self.adSchemaColumns, [None, None, table_name])
        while not a.EOF:
            type = int(a("DATA_TYPE"))
            if type==130:
                isSearch = True
            else:
                isSearch = False
            sql = u'insert into fields_table(列名, 所属表, 类型, 是否查询) values("%s","%s","%d","%d")' % (str(a("COLUMN_NAME")).decode('utf8'), newtableName, type, isSearch)
            self.execute_sql(self.comm_accessdb, sql)
            a.MoveNext()
        a.Close()

class accessdb():
    def __init__(self):
        pass

    @staticmethod
    def exportcursor(sql):   #调用这个函数来输出记录集，待删除！！
        rs = oledb.execute_sql(oledb.comm_accessdb, sql)
        if rs.eof and rs.bof:
            return None     #记录为空
        else:
            return rs

    def del_all_tables(self):        #删除access库的所有表
        a = oledb.conn_accessdb.OpenSchema(oledb.adSchemaTables)
        while not a.EOF:
            if str(a("TABLE_TYPE"))=="TABLE":
                tableName = str(a("TABLE_NAME")).decode('utf8')
                sql = u"drop table [%s];" % tableName
                print u'正在删除[%s]表' % tableName
                oledb.execute_sql(oledb.comm_accessdb, sql)
            a.MoveNext()
        
    def create_manage_table(self):    #创建tables_table,fields_table管理表
        print u'正在创建新表'
        #self.connect_accessdb(self.db_path)
        sql = u"create table tables_table (序号 int identity(1,1), 旧表名 varchar(100), 新表名 varchar(200), 所属文件 varchar(150), 字段连接 text);"
        oledb.execute_sql(oledb.comm_accessdb, sql)
        sql = u"create table fields_table (序号 int identity(1,1), 列名 varchar(100), 类型 int, 是否查询 bit, 所属表 varchar(100));"
        oledb.execute_sql(oledb.comm_accessdb, sql)

    def write_fields_table(self):
        sql1 = u'select [新表名] from tables_table'
        rs1 = oledb.execute_sql(oledb.comm_accessdb, sql1)
        while not rs1.EOF:
            tablename = rs1.Fields.Item(u'新表名').Value
            rs2 = oledb.conn_accessdb.OpenSchema(oledb.adSchemaColumns, [None, None, tablename])
            link_columns_name = ""
            while not rs2.EOF:
                type = int(rs2("DATA_TYPE"))
                
                column_name = str(rs2("COLUMN_NAME"))
                if type==130:
                    isSearch = True
                    link_columns_name += "+[%s]" % column_name
                else:
                    isSearch = False
                sql3 = u'insert into fields_table(列名, 所属表, 类型, 是否查询) values("%s","%s","%d","%d")' % (column_name, tablename, type, isSearch)
                oledb.execute_sql(oledb.comm_accessdb, sql3)
                rs2.MoveNext()
            
            sql4 = u'update tables_table set [字段连接]="%s" where [新表名]="%s"' % (link_columns_name.strip('+'), tablename)
            oledb.execute_sql(oledb.comm_accessdb, sql4)
            rs2.Close()
            rs1.MoveNext()
        rs1.Close()

    def fill_null(self):
        print u"正在填充Null格！"
        sql1 = u'select 列名, 所属表, 类型 from fields_table'
        rs1 = oledb.execute_sql(oledb.comm_accessdb, sql1)
        while not rs1.EOF:
            #pdb.set_trace()
            colname = rs1.Fields.Item(u'列名').Value
            tablename = rs1.Fields.Item(u'所属表').Value
            type = rs1.Fields.Item(u'类型').Value
            if type==130:
                sql2 = u"update [%s] set [%s]=iif(IsNull([%s]), ' ',[%s])" % (tablename, colname, colname, colname) #把所有为Null的值转为空格
                oledb.execute_sql(oledb.comm_accessdb, sql2)
            rs1.MoveNext()
        rs1.Close()



    def search(self, str):   #这是查询台账的关键函数
        sql1 = u'select 新表名,字段连接 from tables_table'
        rs1 = oledb.execute_sql(oledb.comm_accessdb, sql1)
        while not rs1.EOF:
            tablename = rs1.Fields.Item(u'新表名').Value
            addstring = rs1.Fields.Item(u'字段连接').Value
            sql2 = u'select * from [%s] where %s like "%%%s%%"' % (tablename, addstring, str)
            #print sql2
            #pdb.set_trace()
            rs2 = oledb.execute_sql(oledb.comm_accessdb, sql2)
            
            if rs2.EOF==False:
                yield rs2, tablename
            rs1.MoveNext()
    
    def list_fields(self):    #列出数据库中所有表的fields,以表格方式
        sql1 = u'select 新表名 from tables_table'
        rs1 = oledb.execute_sql(oledb.comm_accessdb, sql1)
        #pdb.set_trace()
        while not rs1.EOF:
            tablename = rs1.Fields(0).Value
            #sql2 = u'select t1.新表名,t2.列名  from t2 left join t1 on t1.表名=t2.所属表名 and t1.所属文件名=t2.所属文件名'      #使用左连接来结合t2,t1表格内容，得出新表名与列名的表格
            #sql3 = u'select t2.列名 from (%s) where t1.新表名="%s"' % (sql2, tablename)
            sql2 = u'select 列名 from fields_table where 所属表="%s";' % tablename
            rs2 = oledb.execute_sql(oledb.comm_accessdb, sql2)
            if rs2 is not None:
                yield rs2, tablename
            rs1.MoveNext()

    def tname_manage(self):     #根据t1表生成并返回json，供前端使用  
        #self.connect_access(self.db_path)
        sql = u'select 序号,旧表名,新表名,所属文件 from tables_table'
        rs = oledb.execute_sql(oledb.comm_accessdb, sql)
        reslist = []
        while not rs.EOF:
            resdict = {}
            resdict['id'] = rs.Fields.Item(u'序号').Value
            resdict['old_table_name'] = rs.Fields.Item(u'旧表名').Value
            resdict['new_table_name'] = rs.Fields.Item(u'新表名').Value
            resdict['filename'] = rs.Fields.Item(u'所属文件').Value
            reslist.append(resdict)
            rs.MoveNext()
        return reslist
    
    def tname_write(self, data):    #分析前端返回的json，往t1表写数据。
        for i in data:
            id = int(i['id'])
            new_table_name = i['new_table_name']
            sql = u"update t1 set [新表名]='%s' where [序号]=%d" %(new_table_name, id)
            oledb.execute_sql(oledb.comm_accessdb, sql)

    def close(self):
        oledb.conn_accessdb.Close()

class exceldb():
    def __init__(self, excel_dir):
        self.excel_dir = excel_dir
        self.pattern = re.compile(r'.*[\$|\$\']$')   #正则表示匹配以$及$'结尾的字符串,初步优化得到的excel表名
        pass

    def write_tables_table(self):
        for filename in os.listdir(self.excel_dir):
            pathname = os.path.join(self.excel_dir, filename)
            oledb.connect_excel(pathname)
            print u'\n正在获取%s的表名。' % filename
            a = oledb.conn_excel.OpenSchema(oledb.adSchemaTables)
            #20代表adSchemaTables
             
            while not a.EOF:
                if str(a("TABLE_TYPE"))=="TABLE":
                    #必须加str()进行类型转换，原本是<'type' instance>
                    #有"TABLE" "SYSTEM TABLE" "ACCESS TABLE"三种类型
                    tableName = str(a("TABLE_NAME")).decode('utf8')
                    #filename = splitext(filename)[0]
                    

                    match = self.pattern.search(tableName)
                    if match:   #如果匹配到，则match不为None
                        newtableName = splitext(filename)[0]+"___"+tableName.strip("'$")
                        sql = u'insert into tables_table(旧表名, 新表名, 所属文件) values("%s", "%s", "%s")'% (tableName, newtableName, filename)#这里使用双引号，是为了防止值带单引号时出错。
                        oledb.execute_sql(oledb.comm_accessdb, sql)

                        #self.write_fields_table(self, tableName, newtableName)  #填充fields_table，步骤错误，这样导入的话会把F27~F255的列都导入
                        """待添加:填充tables_table的连接字段，参考step5"""
                a.MoveNext()
            a.Close()
            oledb.conn_excel.Close()

class accessapp():
    def __init__(self, excel_dir):
        self.excel_dir = excel_dir
        pass

    def import_data(self):
        sql = u"select 旧表名,新表名,所属文件 from tables_table"
        rs = oledb.execute_sql(oledb.comm_accessdb, sql)
        #pdb.set_trace()
        while not rs.EOF:
            access_table = rs.Fields.Item(u"新表名").Value
            excel_table = "%s$A:Z" % rs.Fields.Item(u"旧表名").Value.strip("'$")
            filename = rs.Fields.Item(u"所属文件").Value
            filename = os.path.join(self.excel_dir,filename)
            #pdb.set_trace()
            print u'正在导入%s的%s表' % (filename, excel_table)
            
            oledb.accessApplication.DoCmd.TransferSpreadsheet(oledb.acImport, oledb.acSpreadsheetTypeExcel9, 
                            access_table, filename, True, excel_table)


            print '\n'
            rs.MoveNext()


def connect_accessdb(db_path = os.path.join(os.path.dirname(__file__), "base_db.accdb")):   #因为只有本文件才能引用oledb类的静态及类方法，所以外部文件只能通过函数来引用该类的类方法了
    pythoncom.CoInitialize()    #在子进程中应用win32com,得调用这个函数
    
    #db_path = r'C:\Users\devilman\Desktop\execel与access\base_db.accdb'.decode('utf8')
    oledb.connect_accessdb(db_path)
    return accessdb()

def connect_exceldb(excel_dir = r'C:\传输值班台账汇总'.decode('utf8')):
    pythoncom.CoInitialize()
    return exceldb(excel_dir)
    pass

def connect_accessapp(access_path = r'C:\flask_env\project\base_db.accdb'.decode('utf8')):
    pythoncom.CoInitialize()
    #pdb.set_trace()

    #oledb.conn_accessdb.Close()
    #oledb.comm_accessdb.Close()
    #oledb.conn_accessdb = None
    oledb.connect_accessapp(access_path)
    excel_dir = r'C:\传输值班台账汇总'.decode('utf8')
    return accessapp(excel_dir)


if __name__ == "__main__":
    time1 = time.time()

    #step1.init_conn()
    accessdb = connect_accessdb()
    exceldb = connect_exceldb()
    
    accessapp = connect_accessapp()
    
    accessdb.del_all_tables()
    accessdb.create_manage_table()
    exceldb.write_tables_table()
    
    
    accessapp.import_data()
    
    accessdb.write_fields_table()
    
    accessdb.fill_null()

    time2 = time.time()
    print u'用时:%ds' % int(time2-time1)


