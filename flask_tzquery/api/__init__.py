#-*-coding:utf8-*-
from .. import factory

def create_app(setting_override=None, register_security_blueprint=False):
	app = factory.create_app(__name__, __path__, setting_override, 
							register_security_blueprint)
	
	return app