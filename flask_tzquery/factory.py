#-*-coding:utf8-*-
from flask import Flask

from .helpers import register_blueprint
#from settings import template_folder, static_folder
from .flask_session import Session as sess
from flask import appcontext_tearing_down

def create_app(package_name, package_path, setting_override=None,
				register_security_blueprint=True):

	app = Flask(package_name, instance_relative_config=True)

	app.config.from_object("flask_tzquery.settings")
	#app.config.from_pyfile("settings.cfg", silent=True)	#??
	app.config.from_object(setting_override)

	sess(app)	#加入session

	def appcontext_tearing_down_close_excel(sender, **kw):
		sender.config['xlsApp'].app_quit()
		print u"关闭Excel"
		
	appcontext_tearing_down.connect(appcontext_tearing_down_close_excel, app)
	    
	register_blueprint(app, package_name, package_path)

	return app
