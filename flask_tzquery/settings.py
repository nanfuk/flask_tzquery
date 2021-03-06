#-*-coding:utf8-*-
"""
只有大写名称的值才会存储到配置字典对象中
调用时使用:app.config['DATABASE']
"""
import os,sys
import logging

DEBUG = True    #Flask-Script额外库使用的配置文件
SECRET_KEY = "Spe.22"
PATH = u"D:\\Softwares\\flask_env\\flask_tzquery"

LOGCONFIG = "logging.conf"  #Flask-LogConfig额外库使用的配置文件，可以是dict或文件路径
LOGCONFIG_QUEUE = ['Main','Manager','OTN','otn_ring']
LOGCONFIG_REQUESTS_ENABLED = True   # 日志中记录每个请求，使用下面定义的flaskLog这个logger
LOGCONFIG_REQUESTS_LOGGER = 'flask'
LOGCONFIG_REQUESTS_LEVEL = logging.INFO


"""
MySQL参数
"""
USER = 'root'
PWD = '1989'

"""
session配置参数
"""
SESSION_TYPE = 'filesystem'
#DATABASE = os.path.join(os.getcwd(),"database","base_db.mdb")	#使用app.config['DATABASE']调用,os.getcwd()在Apache中是Apache的安装路径。
DATABASE = os.path.join(PATH,"database","base_db.mdb")	#使用app.config['DATABASE']调用,os.getcwd()在Apache中是Apache的安装路径。


"""
更新excel文档的参数
"""
_path = u"D:\\Softwares\\flask_env\\波分端口台账"
VENDER_FILE_DICT = {
						"hw_port":os.path.join(_path, u"华为波分端口资源表格（最新）.xlsm"),
						"zx_port":os.path.join(_path, u"中兴波分端口资源表格（最新）.xlsm"),
						"fh3000_port":os.path.join(_path, u"烽火波分3000端口资源表格（最新）.xlsm"),
						"fh4000_port":os.path.join(_path, u"烽火波分4000端口资源表格（最新）.xlsm")
					}

TABLENAME_DICT = {'750':u'750','baiyunting':u'白云厅','danan':u'大南', 'gangqian':u'岗前','guiguan':u'桂冠','gyy':u'工业园','haijingcheng':u"海景城","hebinnan":u"河滨南","hetai":u"和泰",
    "huaduguangdian":u"花都广电",'jinzhou':u'金州',"kxc":u"科学城","qs":u"七所",'shiji':u"石基",'tyc':u"太阳城",'xinganglou':u"新港楼",'xm':u"夏茅",
    "xsk":u"新时空","yj":u"云景","kexuezhongxinbei":u"科学中心北","changgangzhong":u"昌岗中","dongpushangye":u"东圃商业","dongxing":u"东兴","hualong":u"化龙","jiayi":u"加怡",
    "nanguohuayuan":u"南国花园","nantianguangchang":u"南天广场","yuandong":u"远东","yuehao":u"越豪","zhongqiao":u"中侨","zhujiangguangchang":u"珠江广场","yuntai":u"蕴泰","jinfa":u"金发","taiping":u"太平"}

DISPATCH_TEMPLATE = u"D:\\Softwares\\flask_env\\波分端口台账\\波分资源分配模板.xls"


# class ExceptionHook:
#     instance = None
#
#     def __call__(self, *args, **kwargs):
#         if self.instance is None:
#             from IPython.core import ultratb
#             self.instance = ultratb.FormattedTB(mode='Plain',
#                  color_scheme='Linux', call_pdb=1)
#         return self.instance(*args, **kwargs)
#
# sys.excepthook = ExceptionHook()