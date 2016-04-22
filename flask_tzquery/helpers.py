#-*-coding:utf8-*-
import pkgutil	#Package extension utility(功能)
import importlib
import pdb

from flask import Blueprint

def register_blueprint(app, package_name, package_path):
	"""Register all Blueprint instances on the specified Flask application found
	in all modules for the specified package.

	"""
	rv = []
	#pdb.set_trace()
	for _, name, _ in pkgutil.iter_modules(package_path):
		m = importlib.import_module('%s.%s' % (package_name, name))
		for item in dir(m):
			item = getattr(m, item)
			if isinstance(item, Blueprint):
				app.register_blueprint(item)
			rv.append(item)
	return rv