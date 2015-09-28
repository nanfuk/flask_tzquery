# -*- coding:utf8 -*-

from main import create_app

app = create_app()

if __name__ == "__main__":
    app.run()







"""
import pdb

from flask import Flask, render_template, session
from main.main_blueprint import main_blueprint
from otn.main import otn
from otn_ring.main import otn_ring
from flask_session import Session as sess
#import redis

import excel    #excel模块在上级目录

#r = redis.Redis(host="127.0.0.1", port=6379, db=1)
app = Flask(__name__)   #表示flask在什么位置搜索所需的static与template...
#app.secret_key = "you_guess_it"
#app.config["SESSION_TYPE"] = "redis"
#app.config["SESSION_REDIS"] = r

app.config["SESSION_TYPE"] = "filesystem"
sess(app)

app.register_blueprint(main_blueprint)
app.register_blueprint(otn, url_prefix='/otn')  #加入了url前缀
app.register_blueprint(otn_ring)


@app.route('/dbupdate')
def dbupdate(): #更新数据库指南
    return render_template("db_update.html")

@app.route('/qlc')
def qlc():
    return render_template("qlcpage.html")

if __name__ == "__main__":
    pdb.set_trace()
    app.run(debug=True, host='0.0.0.0', threaded=True)       #设threaded即可以实现多线程访问了
    
"""