#!/usr/bin/python
# -*- coding:utf8 -*-

from flask import Flask, render_template
from main.main_blueprint import main_blueprint


app = Flask(__name__)   #表示flask在什么位置搜索所需的static与template...
app.register_blueprint(main_blueprint)

@app.route('/dbupdate')
def dbupdate(): #更新数据库指南
    return render_template("db_update.html")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', threaded=True)       #设threaded即可以实现多线程访问了
    
