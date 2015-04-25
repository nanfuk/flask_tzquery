#-*-coding:utf8-*-
import win32com.client
from oledb import connect_accessdb
from flask import Flask, g, render_template, request, make_response, Blueprint, session, redirect, url_for, session, current_app
import pdb
import json
import time
import re
import excel
import StringIO
import xlwt
from urllib import unquote   #实现url解码
#from flask_access import sess_interface, app


main_blueprint = Blueprint("main_blueprint", __name__)

def preKey(str):      #对关键字进行预处理
    str = str.strip()

    pattern = re.compile("%")
    str = pattern.sub("%%", str)
    pattern = re.compile(r"\[")   #①r表示字符串的'\'不需转义。②但'['不能直接compile，需要'\'转义才能compile
    str = pattern.sub("%[", str)

    return str.split('*')   #返回的是一个列表

@main_blueprint.before_request      #表示在请求页面之前先连接好数据库
def before_request():
    g.db = connect_accessdb() #返回的是一个类实例
    lt = time.localtime()
    time_format = "%Y-%m-%d %H:%M:%S"
    st = time.strftime(time_format, lt)
    print u"开始时间:%s" % st

@main_blueprint.teardown_request   #是当request的context被弹出时，自动调用的函数。这里是关闭数据库。
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@main_blueprint.route('/')
def entry():
    updatetime = g.db.getUpdatetime()
    #session["time"] = "test"
    return render_template("entry.html",updatetime=updatetime)

@main_blueprint.route('/tzquery')
def tzquery():
    #import pdb
    #pdb.set_trace()
    #print session["time"]
    #lt = time.localtime()
    #time_format = "%Y-%m-%d %H:%M:%S"
    #st = time.strftime(time_format, lt)
    #current_time = time.time()
    if current_app.session_interface.judge_attack(current_app, request):
        return u"访问太频繁！"

    time1 = time.time()
    session["time"] = time1

    current_app.session_interface.save_session_without_response(current_app, session)
    
    #if request.remote_addr == "10.117.194.222": #黑名单
    #    return(u"-_-!!")

    searchword = request.args.get('key', '')    #根据网页的设置编码来得出的是Unicode编码
    area = request.args.get('area', '')
    version = request.args.get("version", '')

    if version!="1.0":
        return(u"主页已更新，请刷新主页。")

    keyList = preKey(searchword)
    rs_generator = g.db.search(keyList, area)    #返回的是一个迭代器，调用next()来获取数据

    sum = 0
    entries = []
    for rs,tablename in rs_generator:        
        counts=rs.RecordCount
        #pdb.set_trace()
        entries.append(dict(rs=rs,tablename=tablename,counts=counts))
        sum += counts
    time2 = time.time()
    print u"%s-->%s" % (searchword, area)
    print u"查询时间:%.2f秒" % (time2-time1)

    if sum==0:
        return render_template("not_found.html")
    elif sum>500:
        return render_template("too_many.html",sum=sum)
    else:
        pattern = re.compile(r"\\")   #这个正则是给模板用的。
        searchword = pattern.sub(r"\\\\",searchword)
        return render_template('show_entries.html', entries=entries,keyList=keyList,keys=len(keyList),searchword=searchword, area=area)
        #keys为关键字数目，因为在模板中无法使用len方法


@main_blueprint.route('/export')
def export_xls():
    searchword = request.args.get('key', '')
    keyList = preKey(searchword)
    #pdb.set_trace()
    area = request.args.get("area", "") 

    rs_generator = g.db.search(keyList, area)

    wb = xlwt.Workbook()
    wb.encoding = "gbk"
    
    lt = time.localtime()
    ISOTIMEFORMAT = '%H_%M_%S'
    ft = time.strftime(ISOTIMEFORMAT, lt)

    pattern = re.compile(r".*___")

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

@main_blueprint.route('/list_fields')
def listFields():
    rs_generator = g.db.list_fields()
    entries = [dict(rs=rs,tablename=tablename) for rs,tablename in rs_generator]
    #pdb.set_trace()
    return render_template('list_fields.html', entries=entries)

@main_blueprint.route('/tname_manage',methods=['POST', 'GET'])
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
