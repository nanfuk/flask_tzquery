#-*-coding:utf8-*-
from flask import Flask

from .helpers import register_blueprint
from settings import template_folder, static_folder

def create_app(package_name, package_path, setting_override=None,
				register_security_blueprint=True):

	app = Flask(package_name, instance_relative_config=True)

	app.config.from_object("flask_tzquery.settings")
	#app.config.from_pyfile("settings.cfg", silent=True)	#??
	app.config.from_object(setting_override)

	register_blueprint(app, package_name, package_path)

	return app
