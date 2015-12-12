#-*-coding:utf8-*-

from flask.ext.script import Manager	#安装Flask-Script
from flask_tzquery.api import create_app

manager = Manager(create_app())

if __name__ == '__main__':
	manager.run()