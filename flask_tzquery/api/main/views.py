#-*-coding:utf8-*-
#import win32com.client
#from oledb import connect_accessdb
from flask import abort, g, render_template, request, make_response, session, redirect, url_for, current_app
import pdb
import json
import time
import re
#import excel    #??为什么要导入
import StringIO
import xlwt
import hashlib
import logging

import redis_component

from urllib import unquote   #实现url解码

from . import bp
from .other import preKey, resumeKey
#from ...odbc import accessdb
#from ...oledb import accessdb
from ...db_engine.oledb import accessdb

#main_blueprint = Blueprint("main_blueprint", __name__)
"""
def preKey(str):      #对关键字进行预处理
    str = str.strip()

    pattern = re.compile("%")
    str = pattern.sub("%%", str)
    pattern = re.compile(r"\[")   #①r表示字符串的'\'不需转义。②但'['不能直接compile，需要'\'转义才能compile
    str = pattern.sub("%[", str)

    return str.split('*')   #返回的是一个列表
"""

logger = logging.getLogger('tzquery')

# @bp.before_request      #表示在请求页面之前先连接好数据库
# def before_request():
    # g.db = accessdb(current_app.config['DATABASE']) #返回的是一个类实例
    # a = 0/0
    # g.st = time.strftime("%H:%M:%S", time.localtime())

# @bp.teardown_request   #是当request的context被弹出时，自动调用的函数。这里是关闭数据库。
# def teardown_request(exception):
    # db = getattr(g, 'db', None)
    # if db is not None:
        # db.close()

@bp.route('/')
def entry():
    #updatetime = g.db.getUpdatetime()
    #session["time"] = "test"
    updatetime = "xxxx"
    return render_template("entry.html",updatetime=updatetime)

@bp.route('tzquery', methods=['GET'])
def tzquery():
    start = time.time()
    key = request.args.get('key',"")    #根据网页的设置编码来得出的是Unicode编码
    try:
        key = key.encode("utf8")
    except:
        abort(500)
    area = request.args.get('area',"")
    version = request.args.get("version", '')
    # ToDo 判断key的编码格式
    if key!="" and area!="":
        keywords = key.split("*")
        records = redis_component.query(area, keywords)
        rowCount = 0
        for table in records:
            rowCount += len(records[table]["rowData"])
        
        end = time.time()
        logger.info(u"%s    关键字:%s->%s    用时:%.2f" % (request.remote_addr, area, key.decode("utf8"), end-start))
        return render_template('show_entries.html', key=key, area=area, records=records, rowCount=rowCount)
    abort(500)    #ToDo

@bp.route('getQueryResult', methods=['POST'])
def getQueryResult():
    start = time.time()
    keywords = request.form.get("keywords")
    area = request.form.get("area")
    if "keywords" and "area":
        keywords = json.loads(keywords)
        if "" in keywords:
            abort(500)
        try:
            keywords = [i.encode('utf8') for i in keywords] # 传过来的是Unicode，转为utf8传给redis
        except:
            abort(500)
        records = redis_component.query(area, keywords)
        end = time.time()
        logger.info(u"%s    关键字:%s    用时:%.2f" % (request.remote_addr, request.form.get("keywords"), end-start))
        
        return json.dumps(records,ensure_ascii=False)
    abort(500)    #ToDo


@bp.route('export')
def export():
    key = request.args.get('keywords', "")
    area = request.args.get("area", "")
    try: # POST请求的key要考虑url编码的问题
        key = key.encode("utf8")
    except:
        abort(500)
    if key!="" and area!="":
        keywords = key.split("*")
        records = redis_component.query(area, keywords, preRender=False)    #preRender设为False，关键字不加span标记
        resp = export2xls(records)
        # try:
            # resp = export2xls(records)
        # except:
            # logger.error(u"%s   导出表格失败，关键字:%s->%s" % (request.remote_addr, area, key.decode("utf8")))
            # abort(500)
        logger.info(u"%s    导出表格，关键字:%s->%s" % (request.remote_addr, area, key.decode("utf8")))
        return resp
    abort(500)

def export2xls(data):
    wb = xlwt.Workbook(encoding="utf8")
    # wb.encoding = "utf8"
    
    lt = time.localtime()
    ISOTIMEFORMAT = '%H_%M_%S'
    ft = time.strftime(ISOTIMEFORMAT, lt)

    for tablename,content in data.items():
        row = col = 0
        ws = wb.add_sheet(content["tabIndex"])
        ws.write(row, col, tablename)
        row += 1
        for colName in content["colName"]:
            ws.write(row,col,colName)
            col += 1
        col = 0
        row += 1
        for rowData in content["rowData"]:
            for cellData in rowData:
                ws.write(row,col,cellData)
                col += 1
            col = 0
            row += 1
    sio = StringIO.StringIO()
    wb.save(sio)        #这点很重要，传给save函数的不是保存文件名，而是一个StringIO流

    
    resp = make_response(sio.getvalue(), 200)
    resp.headers['Content-type'] = 'application/vnd.ms-excel'  #指定返回的类型,浏览器就会提示要下载的文件是excel文件
    resp.headers['Transfer-Encoding'] ='chunked'    # 表示输出的内容长度不能确定
    resp.headers['Content-Disposition'] = 'attachment;filename="%s.xls"' % ft #设定用户浏览器显示的保存文件名

    return resp


    # pattern = re.compile(r".*__")

    # for rs,tablename in rs_generator: 
    #     row = 0
    #     col = 0
    #     #pdb.set_trace()
    #     if len(tablename) > 31:
    #         tablename = pattern.sub("", tablename)  #excel支持的最大长度表名是31字节。替换掉文件名___来缩减长度。

    #     ws = wb.add_sheet(tablename)
    #     for field in rs.Fields:
    #         ws.write(row,col,field.name)
    #         col += 1
    #     col = 0
    #     #style = xlwt.XFStyle()
    #     #style.num_format_str = "D-MMM-YY"

    #     while not rs.EOF:
    #         for field in rs.Fields:
    #             try:
    #                 ws.write(row+1,col,rs.Fields.Item(field.name).Value)
    #             except: #解决xlwt无法写入type<'time'>的问题，把时钟类型强制转为字符串类型
    #                 ws.write(row+1,col,str(rs.Fields.Item(field.name).Value))
    #             col += 1
    #         rs.MoveNext()
    #         col = 0
    #         row += 1

    # sio = StringIO.StringIO()
    # wb.save(sio)        #这点很重要，传给save函数的不是保存文件名，而是一个StringIO流

    
    # resp = make_response(sio.getvalue(), 200)
    # resp.headers['Content-type'] = 'application/vnd.ms-excel'  #指定返回的类型,浏览器就会提示要下载的文件是excel文件
    # resp.headers['Transfer-Encoding'] ='chunked'    # 表示输出的内容长度不能确定
    # resp.headers['Content-Disposition'] = 'attachment;filename="%s.xls"' % ft #设定用户浏览器显示的保存文件名
    
    # return resp
    #xlsBook.Close(False)
    #xlsApp.Quit()

@bp.route('/list_fields')
def listFields():
    rs_generator = g.db.list_fields()
    entries = [dict(rs=rs,tablename=tablename) for rs,tablename in rs_generator]
    #pdb.set_trace()
    return render_template('list_fields.html', entries=entries)

@bp.route('/tname_manage',methods=['POST', 'GET'])
def tnameManage():
    if request.method == 'GET':
        t1_json = g.db.tname_manage()
        return render_template('tname_manage.html', data=t1_json)
    
    #data = request.form  #这是一个ImmutableMultiDict类型的数据,形式:[{'传回来的数据',u''}]。不好使用。
    data = request.get_json(force=True)   #这能把返回来的数据转为list
    #print type(data)
    #pdb.set_trace()
    #print data
    #print json.loads(data)
    g.db.tname_write(data)
    t1_json = g.db.tname_manage()
    return render_template('tname_manage.html', data=t1_json)
"""
@main_blueprint.route('/test')
def test():
    #rs_generator = g.db.search([u"新时空"], "01")    #返回的是一个迭代器，调用next()来获取数据
    return g.db.search([u"新时空"], "01")
"""
@bp.route('/client_names')
def clients_name():
    return g.db.get_client_json()

@bp.route('/test')
def test():
    return render_template('SilverlightApplication7TestPage.html')

@bp.route("managedb", methods=["GET","POST"])
def managedb():
    if request.method == "POST":
        print "begin"
        start = time.time()
        action = request.form.get("action")

        if action == "add": # 新增excel
            classified = request.form.get("classified")
            if classified:
                for k, v in request.files.items():
                    file = request.files[k]
                    updateTime = str(time.time()) # 传入字符串，不能是浮点数
                    lastModified = request.form.get("lastModified"+k,"")
                    size = request.form.get("size"+k,"")
                    
                    f = StringIO.StringIO()
                    f.write(file.read())
                    print u"读取文件用时:%.2f" % (time.time()-start)

                    redis_component.importMemoryExcel(
                        f               = f,
                        filename        = file.filename,
                        classified      = classified,
                        updateTime      = updateTime,
                        lastModified    = lastModified,
                        size            = size
                    )
                    f.close()
                return "add success"
            return "add error"

        elif action == "del": # 删除excel
            wbIndexList = request.form.getlist("wbIndexList[]")
            if wbIndexList:
                for wbIndex in wbIndexList:
                    redis_component.delWbInRedis(wbIndex)
                return "del success"
            return "del error"

    # 通过get请求得到工作簿列表
    fileDict = redis_component.getFileNameDict()
    data = []
    for k,v in fileDict.items():    # utf8编码的内容
        wbName          = v.get("wbName","")
        updateTime      = v.get("updateTime","")
        lastModified    = v.get("lastModified","")
        size            = v.get("size","")
        try:
            updateTime = time.strftime("%y-%m-%d %H:%M",time.localtime(float(updateTime)))
        except:
            pass

        try:
            lastModified = time.strftime("%y-%m-%d %H:%M",time.localtime(float(lastModified)/1000))
        except:
            pass

        try:
            size = float(size)
            if size < 1024:
                size = "%d B" % size
            elif size < 1024*1024:
                size = "%d KB" % round(size/1024)
            else:
                size = "%.2f MB" % round(size/(1024*1024), 2)
        except:
            pass

        data.append({
            "wbIndex":k,
            "wbName":wbName,
            "size":size,
            "updateTime":updateTime,
            "lastModified":lastModified
        })
    return json.dumps(data)
