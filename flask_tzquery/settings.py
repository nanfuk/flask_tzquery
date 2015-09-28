#-*-coding:utf8-*-
#只有大写名称的值才会存储到配置字典对象中
import os

DEBUG = False
SECRET_KEY = "Spe.22"

template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)),"frontend\\templates")
static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)),"frontend\\statics")
#这样设置无法通过app.config.from_object('**')更改template目录
#这样是没法存入app.config 这个字典的
#只是为了import
#print TEMPLATE_FOLDER