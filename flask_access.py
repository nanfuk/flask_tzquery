#!/usr/bin/python
# -*- coding:utf8 -*-
import win32com.client
from oledb import connect_accessdb
from flask import Flask, g, render_template, request
import pdb
import json

#adCmdText = 1

app = Flask(__name__)   #表示flask在什么位置搜索所需的static与template...



@app.before_request      #表示在请求页面之前先连接好数据库
def before_request():
    g.db = connect_accessdb() #返回的是一个类实例

@app.teardown_request   #是当request的context被弹出时，自动调用的函数。这里是关闭数据库。
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        #pdb.set_trace()
        db.close()

@app.route('/')
def entry():
    return render_template("entry.html")

@app.route('/tzquery')
def tzquery():
    searchword = request.args.get('key', '').strip()
    #pdb.set_trace()
    rs_generator = g.db.search(searchword)    #返回的是一个迭代器，调用next()来获取数据
    #pdb.set_trace()
    entries = [dict(rs=rs,tablename=tablename) for rs,tablename in rs_generator]
    #pdb.set_trace()
    if entries==[]:
        return render_template("not_found.html")
    else:
        return render_template('show_entries.html', entries=entries,searchword=searchword)

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
    app.run(debug=True,host='0.0.0.0')
