#-*-coding:utf8-*-

from flask.ext.script import Manager	#安装Flask-Script
from flask_tzquery.api import create_app

app = create_app()
manager = Manager(create_app())


if __name__ == '__main__':
	manager.run()	#怎么改host为0.0.0.0，python manage.py runserver -h 0.0.0.0