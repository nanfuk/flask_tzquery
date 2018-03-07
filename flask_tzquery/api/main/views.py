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
    
    # time1 = time.time()
    # if current_app.session_interface.judge_attack(current_app, request):
    #     session["time"] = time1
    #     current_app.session_interface.save_session_without_response(current_app, session)
    #     logger.warn(u"%s 访问频繁", request.remote_addr)
    #     return u"访问太频繁！3秒后再查询~.~"

    # session["time"] = time1

    # current_app.session_interface.save_session_without_response(current_app, session)

    # #if request.remote_addr == "10.117.194.222": #黑名单
    # #    return(u"-_-!!")
    searchword = request.args.get('key', '')    #根据网页的设置编码来得出的是Unicode编码
    # searchword = "*".join([i.strip(" ") for i in searchword.split("*")])    #去除空格,ToDo前端来做
    area = request.args.get('area', '')
    version = request.args.get("version", '')

    # if version!="1.0":
    #     return(u"主页已更新，请刷新主页。")

    # searchwordList = searchword.split("*")
    # keyList = preKey(searchwordList)    # 预处理字符串，传给数据库查询
    # # rs_generator = g.db.search(keyList, area)    #返回的是一个迭代器，调用next()来获取数据
    
    # sum = 0
    # entries = []
    """
    #以下为easyui的展示方式
    fields_A_to_Z = [chr(x) for x in range(65,91)]
    for rs, columns, tablename in rs_generator:        
        counts= len(rs) #rs是一个列表
        columns = zip(fields_A_to_Z,columns)    #[('A','列名一'),('B','列名二')...]
        if counts>0:
            entries.append(dict(rs=rs,tablename=tablename,columns=columns))
        sum += counts
    """
    # for rs,tablename in rs_generator:        
        # counts=rs.RecordCount
        # entries.append(dict(rs=rs,tablename=tablename,counts=counts,hash=hashlib.md5(tablename.encode('gbk')).hexdigest()))
        # sum += counts
    # tablename = "test"
    # records = redis_component.query(keyList[0])


    # time2 = time.time()
    # logger.info(u"%s %s->%s 时间:%.2fs，", request.remote_addr, area, searchword, time2-time1)

    # keyList = resumeKey(keyList)     # 把给数据库的字符串还原为网页能识别高亮显示的字符
    return render_template('show_entries.html', searchword=searchword, area=area)
    # if sum==0:
    #     return render_template("not_found.html")
    # elif sum>1000:
    #     return render_template("too_many.html",sum=sum)
    # else:
    #     pattern = re.compile(r"\\")   #这个正则是给模板用的。
    #     searchword = pattern.sub(r"\\\\",searchword)  #模板中是继承g的,尝试改下
    #     #return render_template('show_entries.html', entries=entries,keyList=keyList,keys=len(keyList),searchword=searchword, area=area)
    #     return render_template('show_entries.html', entries=entries,keyList=keyList,keys=len(keyList),searchword=searchword, area=area)
        # return render_template('show_entries.html', entries=entries,keyList=keyList,keys=len(keyList), area=area)
        #keys为关键字数目，因为在模板中无法使用len方法
    """
    #以下为easyui通过ajax加载表格来提升访问速度的代码
    if request.method == 'GET':
        searchword = request.args.get('key', '')    #根据网页的设置编码来得出的是Unicode编码
        area = request.args.get('area', '')
        version = request.args.get("version", '')
        index = 0   #传给js的，告知其下次请求的表号
        param = json.dumps({'searchword':searchword,'area':area,'index':index})
        return render_template('test_easyui.html', param=param)

    searchword = request.form['searchword']    #根据网页的设置编码来得出的是Unicode编码
    keyList = preKey(searchword)
    area = request.form['area'] 

    index = int(request.form['index'])
    json_content = g.db.search_by_table_index(keyList, area, index) #这得返回json值
    return json_content
    """

@bp.route('getQueryResult', methods=['POST'])
def getQueryResult():
    start = time.time()
    # import pdb;pdb.set_trace()
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
        end = time.time()
        records = redis_component.query(area, keywords)
        
        logger.info(u"%s    关键字:%s    用时:%.2f" % (request.remote_addr, request.form.get("keywords"), end-start))
        
        return json.dumps(records,ensure_ascii=False)
    abort(500)    #ToDo


@bp.route('/export')
def export_xls():
    searchword = request.args.get('key', '')
    keyList = preKey(searchword)
    area = request.args.get("area", "") 

    rs_generator = g.db.search(keyList, area)

    wb = xlwt.Workbook()
    wb.encoding = "gbk"
    
    lt = time.localtime()
    ISOTIMEFORMAT = '%H_%M_%S'
    ft = time.strftime(ISOTIMEFORMAT, lt)

    pattern = re.compile(r".*__")

    for rs,tablename in rs_generator: 
        row = 0
        col = 0
        #pdb.set_trace()
        if len(tablename) > 31:
            tablename = pattern.sub("", tablename)  #excel支持的最大长度表名是31字节。替换掉文件名___来缩减长度。

        ws = wb.add_sheet(tablename)
        for field in rs.Fields:
            ws.write(row,col,field.name)
            col += 1
        col = 0
        #style = xlwt.XFStyle()
        #style.num_format_str = "D-MMM-YY"

        while not rs.EOF:
            for field in rs.Fields:
                try:
                    ws.write(row+1,col,rs.Fields.Item(field.name).Value)
                except: #解决xlwt无法写入type<'time'>的问题，把时钟类型强制转为字符串类型
                    ws.write(row+1,col,str(rs.Fields.Item(field.name).Value))
                col += 1
            rs.MoveNext()
            col = 0
            row += 1

    sio = StringIO.StringIO()
    wb.save(sio)        #这点很重要，传给save函数的不是保存文件名，而是一个StringIO流

    
    resp = make_response(sio.getvalue(), 200)
    resp.headers['Content-type'] = 'application/vnd.ms-excel'  #指定返回的类型,浏览器就会提示要下载的文件是excel文件
    resp.headers['Transfer-Encoding'] ='chunked'    # 表示输出的内容长度不能确定
    resp.headers['Content-Disposition'] = 'attachment;filename="%s.xls"' % ft #设定用户浏览器显示的保存文件名
    
    return resp
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
