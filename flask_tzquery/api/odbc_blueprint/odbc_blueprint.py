#-*-coding:utf8-*-
import win32com.client
from odbc import accessdb
from flask import Flask, g, render_template, request, make_response, Blueprint, session, redirect, url_for, session, current_app
import pdb
import json

odbc_blueprint = Blueprint("odbc_blueprint", __name__)

@odbc_blueprint.before_request      #表示在请求页面之前先连接好数据库
def before_request():
    g.db = accessdb() #返回的是一个类实例

@odbc_blueprint.teardown_request   #是当request的context被弹出时，自动调用的函数。这里是关闭数据库。
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@odbc_blueprint.route('/client_names')
def client_names():
    return g.db.get_client_json()
