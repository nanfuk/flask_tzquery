#!/usr/bin/python
# -*- coding:utf8 -*-
import win32com.client
from oledb import connect_accessdb
from flask import Flask, g, render_template, request, make_response
import pdb
import json
import time
import re
from flask import request_started     #这是信号
import excel
import StringIO
import xlwt


app = Flask(__name__)   #表示flask在什么位置搜索所需的static与template...


def preKey(str):      #对关键字进行预处理
    str = str.strip()

    pattern = re.compile("%")
    str = pattern.sub("%%", str)
    pattern = re.compile(r"\[")   #①r表示字符串的'\'不需转义。②但'['不能直接compile，需要'\'转义才能compile
    str = pattern.sub("%[", str)

    return str.split('*')

@app.before_request      #表示在请求页面之前先连接好数据库
def before_request():
    g.db = connect_accessdb() #返回的是一个类实例
    print u"开始时间:%d" % int(time.time())

@app.teardown_request   #是当request的context被弹出时，自动调用的函数。这里是关闭数据库。
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        print u"关闭数据库"
        db.close()

@app.route('/')
def entry():
    updatetime = g.db.getUpdatetime()
    return render_template("entry.html",updatetime=updatetime)

@app.route('/tzquery')
def tzquery():
    #before_request()
    #pdb.set_trace()
    time1 = time.time()
    searchword = request.args.get('key', '')

    keyList = preKey(searchword)
    rs_generator = g.db.search(keyList)    #返回的是一个迭代器，调用next()来获取数据

    sum = 0
    entries = []
    for rs,tablename in rs_generator:        
        counts=rs.RecordCount
        #pdb.set_trace()
        entries.append(dict(rs=rs,tablename=tablename,counts=counts))
        sum += counts
    time2 = time.time()
    print time2-time1

    if sum==0:
        return render_template("not_found.html")
    elif sum>400:
        return render_template("too_many.html",sum=sum)
    else:
        pattern = re.compile(r"\\")   #这个正则是给模板用的。
        searchword = pattern.sub(r"\\\\",searchword)
        return render_template('show_entries.html', entries=entries,keyList=keyList,keys=len(keyList),searchword=searchword)
        #keys为关键字数目，因为在模板中无法使用len方法

@app.route('/export')
def export_xls():
    searchword = request.args.get('key', '')
    keyList = preKey(searchword)
    #pdb.set_trace()
    rs_generator = g.db.search(keyList)

    wb = xlwt.Workbook()
    wb.encodeing = "gbk"
    
    lt = time.localtime()
    ISOTIMEFORMAT = '%X'
    ft = time.strftime(ISOTIMEFORMAT, lt)

    for rs,tablename in rs_generator:        
        #counts=rs.RecordCount
        #pdb.set_trace()
        row = 0
        col = 0
        #pdb.set_trace()
        ws = wb.add_sheet(tablename)
        for field in rs.Fields:
            ws.write(row,col,field.name)
            col += 1
        col = 0
        while not rs.EOF:
            for field in rs.Fields:
                ws.write(row+1,col,rs.Fields.Item(field.name).Value)
                col += 1
            rs.MoveNext()
            col = 0
            row += 1
    #ws = wb.add_sheet("1")
    #ws.write(0,1,u"测试")
    sio = StringIO.StringIO()
    wb.save(sio)        #这点很重要，传给save函数的不是保存文件名，而是一个StringIO流

    
    resp = make_response(sio.getvalue(), 200)
    resp.headers['Content-type'] = 'application/vnd.ms-excel'  #指定返回的类型,浏览器就会提示要下载的文件是excel文件
    resp.headers['Transfer-Encoding'] ='chunked'    # 表示输出的内容长度不能确定
    resp.headers['Content-Disposition'] = 'attachment;filename="%s.xls"' % ft #设定用户浏览器显示的保存文件名
    
    return resp
    #xlsBook.Close(False)
    #xlsApp.Quit()

@app.route('/dbupdate')
def dbupdate(): #更新数据库指南
    return render_template("db_update.html")

@app.route('/list_fields')
def listFields():
    rs_generator = g.db.list_fields()
    entries = [dict(rs=rs,tablename=tablename) for rs,tablename in rs_generator]
    #pdb.set_trace()
    return render_template('list_fields.html', entries=entries)

@app.route('/tname_manage',methods=['POST', 'GET'])
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

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', threaded=True, processes=1)       #设threaded即可以实现多线程访问了
    
