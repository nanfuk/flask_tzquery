#-*-coding:utf8-*-

# from flask.ext.script import Manager    #安装Flask-Script
from flask_tzquery.api import create_app
import os, sys
# import logging, logging.config

# logging.config.fileConfig('logging.conf')
# logger = logging.getLogger('Manager')
# logger.info(u"程序启动")
from flask.ext.logconfig import LogConfig


os.environ['PYTHON_EGG_CACHE'] = '/tmp/.python-eggs'
# abspath = os.path.dirname(__file__)
# sys.path.append(abspath)

# os.chdir(abspath) #改变当前的工作目录，里面的参数为：要设置的目录

app = create_app()
# logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
LogConfig(app)
# logcfg.stop_listeners(app)

# manager = Manager(create_app())

# from werkzeug.debug import DebuggedApplication
# app = DebuggedApplication(app, True)
@app.errorhandler(500)
def internal_server_error(e):
    import logging
    logging.getLogger('Manager').exception("error:500:%s", e)
    return render_template('500.html'), 500


if __name__ == '__main__':
    
    # manager.run()   #怎么改host为0.0.0.0，python manage.py runserver -h 0.0.0.0
    app.run(debug=False)