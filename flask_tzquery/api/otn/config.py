#-*-coding:utf8-*-
import os.path

_path = u"D:\\flask_env\波分端口台账"
HW_PORT_FILEPATH = os.path.join(_path, u"烽火波分3000端口资源表格（最新）.xlsx")
FH3000_PORT_FILEPATH = os.path.join(_path, u"烽火波分4000端口资源表格（最新）.xls") 
FH4000_PORT_FILEPATH = os.path.join(_path, u"华为波分端口资源表格（最新）.xls")
ZX_PORT_FILEPATH = os.path.join(_path, u"中兴波分端口资源表格（最新）.xlsx")

vender_file_dict = {
						"hw_port":HW_PORT_FILEPATH,
						"zx_port":ZX_PORT_FILEPATH,
						"fh300_port":FH3000_PORT_FILEPATH,
						"fh4000_port":FH4000_PORT_FILEPATH
					}

tablename_dict = {'750':u'750','baiyunting':u'白云厅','danan':u'大南', 'gangqian':u'岗前','guiguan':u'桂冠','gyy':u'工业园','haijingcheng':u"海景城","hebinnan":u"河滨南","hetai":u"和泰",
    "huaduguangdian":u"花都广电",'jinzhou':u'金州',"kxc":u"科学城","qs":u"七所",'shiji':u"石基",'tyc':u"太阳城",'xinganglou':u"新港楼",'xm':u"夏茅",
    "xsk":u"新时空","yj":u"云景","kexuezhongxinbei":u"科学中心北","changgangzhong":u"昌岗中","dongpushangye":u"东圃商业","dongxing":u"东兴","hualong":u"化龙","jiayi":u"加怡",
    "nanguohuayuan":u"南国花园","nantianguangchang":u"南天广场","yuandong":u"远东","yuehao":u"越豪","zhongqiao":u"中侨","zhujiangguangchang":u"珠江广场","yuntai":u"蕴泰"}