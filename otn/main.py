#-*-coding:utf8-*-

import xlrd
from flask import Flask, Blueprint, g, request, jsonify, json
import pdb
import MySQLdb


otn = Blueprint("otn", __name__)


class data_strucure():		#数据结构
	def __init__(self, table, table_row):
		#table = data.sheet_by_name(table_name)
		self.jf = table.cell(table_row, 1).value	#B列，机房名
		self.jjh = table.cell(table_row, 8).value		#I列，机架号
		self.jkh = str(table.cell(table_row, 9).value).rstrip(".0")		#J列，机框号，数字
		self.cwh = str(table.cell(table_row, 10).value).rstrip(".0")	#K列，槽位号，数字
		self.dbm = table.cell(table_row, 11).value	#L列，单板名
		self.dkh = str(table.cell(table_row, 12).value).rstrip(".0")	#M列，端口号，数字
		self.odf = table.cell(table_row, 15).value	#P列，ODF架位
		self.bd = table.cell(table_row, 6).value		#G列，波道
		self.lyxx = table.cell(table_row, 4).value	#E列，环路路由信息

@otn.before_request
def before_request():
	try:
		vender = request.form['vender']
		if vender=="hw":
			workbook_path = r"..\波分端口台账\华为波分端口资源表格（最新）.xls".decode("utf8")	#相对路径
		elif vender=="fh3000":
			workbook_path = r"..\波分端口台账\烽火波分3000端口资源表格（最新）.xlsx".decode("utf8")
		elif vender=="fh4000":
			workbook_path = r"..\波分端口台账\烽火波分4000端口资源表格（最新）.xls".decode("utf8")
		elif vender=="zx":
			workbook_path = r"..\波分端口台账\中兴波分端口资源表格（最新）.xlsx".decode("utf8")
		g.wb = xlrd.open_workbook(workbook_path)
	except:
		
		#g.conn = MySQLdb.connect(host="127.0.0.1",user="root",passwd="lanbinbin1989",db="fh300_port", charset='gbk') 
		g.conn = MySQLdb.connect(host="127.0.0.1",user="root",passwd="lanbinbin1989",charset='gbk') 
		g.cursor = g.conn.cursor()

@otn.teardown_request   #是当request的context被弹出时，自动调用的函数。这里是关闭数据库。
def teardown_request(exception):
    wb = getattr(g, 'wb', None)
    conn = getattr(g, 'conn', None)
    if wb is not None:
        #wb.close()		#待分析是否这样关闭
        pass
    if conn is not None:
    	conn.close()
    	
@otn.route('/get_tree_json')
def tree():
	tablename_dict = {'750':u'750','baiyunting':u'白云厅','danan':u'大南', 'gangqian':u'岗前','guiguan':u'桂冠','gyy':u'工业园','haijingcheng':u"海景城","hebinnan":u"河滨南","hetai":u"和泰",
	"huaduguangdian":u"花都广电",'jinzhou':u'金州',"kxc":u"科学城","qs":u"七所",'shiji':u"石基",'tyc':u"太阳城",'xinganglou':u"新港楼",'xm':u"夏茅",
	"xsk":u"新时空","yj":u"云景","kexuezhongxinbei":u"科学中心北","changgangzhong":u"昌岗中","dongpushangye":u"东圃商业","dongxing":u"东兴","hualong":u"化龙","jiayi":u"加怡",
	"nanguohuayuan":u"南国花园","nantianguangchang":u"南天广场","yuandong":u"远东","yuehao":u"越豪","zhongqiao":u"中侨","zhujiangguangchang":u"珠江广场"}
	list_data = []

	vender_db_list = [('fh300_port',u"烽火3000"),('hw_port',u"华为"),('fh4000_port',u"烽火4000"),('zx_port',u"中兴")]

	for vender_db,vender_name in vender_db_list:
		dict_data = {}
		dict_data.setdefault("id",vender_db)	#使用字典的setdefault来添加项值对
		dict_data.setdefault("text",vender_name)	#字典取值
		g.cursor.execute("select table_name from information_schema.tables where table_schema='%s'" % vender_db)
		for tablename in g.cursor.fetchall():	#这里是添加列表，并配合列表的append来增长列表，可以看笔记记录的字典操作
			dict_data.setdefault("children",[]).append({"text":tablename_dict[tablename[0]], "id":tablename[0],"attributes":{"parent":"%s" % vender_db}})
			#为了能得到combotree选取值的父节点，加了attributes属性，使用方法:node.attributes.parent
	
		list_data.append(dict_data)

	return json.dumps(list_data)


@otn.route('/dispatch', methods=['POST'])
def dispatch():
	source_table_name = request.form['atable']
	source_table_row = int(request.form['ano'])
	dest_table_name = request.form['ztable']
	dest_table_row = int(request.form['zno'])
	vender = request.form['vender']

	source_table = g.wb.sheet_by_name(source_table_name)
	dest_table = g.wb.sheet_by_name(dest_table_name)

	source_route_data_structure = data_strucure(source_table, source_table_row)
	dest_route_data_structure = data_strucure(dest_table, dest_table_row)

	route = "---##---*%s(%s-%s)%s-%s-%s(ODF:%s)---%s---%s---%s---%s(%s-%s)%s-%s-%s(ODF:%s)*---##---" %(source_route_data_structure.jf,
																									  source_route_data_structure.jjh,
																									  source_route_data_structure.jkh,
																									  source_route_data_structure.cwh,
																									  source_route_data_structure.dbm,
																									  source_route_data_structure.dkh,
																									  source_route_data_structure.odf,
																									  source_route_data_structure.bd,
																									  source_route_data_structure.lyxx,
																									  dest_route_data_structure.bd,
																									  dest_route_data_structure.jf,
																									  dest_route_data_structure.jjh,
																									  dest_route_data_structure.jkh,
																									  dest_route_data_structure.cwh,
																									  dest_route_data_structure.dbm,
																									  dest_route_data_structure.dkh,
																									  dest_route_data_structure.odf)
	#pdb.set_trace()
	return route


@otn.route('/port', methods=['GET','POST'])
def otn_port():
	datas = []
	field_names = ["no","anode","direction","znode","route","wavelength","index","remark"]
	if request.method=='GET':
		dbname = request.args.get('vender_otn', '')
		tablename = request.args.get('jf_name', '')
		wavelength = request.args.get('wavelength_val', "")
		if wavelength !="":
			g.cursor.execute(u"select 序号, 站点（本端落地）, 方向, 对端落地, 波道路由, 对应的高端系统时隙编号（波长编号）, 广州联通电路编号, 备注 from %s.%s where 对应的高端系统时隙编号（波长编号） like '_%s%%'" % (dbname,tablename,wavelength)) 
		else:
			g.cursor.execute(u"select 序号, 站点（本端落地）, 方向, 对端落地, 波道路由, 对应的高端系统时隙编号（波长编号）, 广州联通电路编号, 备注 from %s.%s" % (dbname,tablename)) 
	else:
		g.cursor.execute(u"select 序号, 站点（本端落地）, 方向, 对端落地, 波道路由, 对应的高端系统时隙编号（波长编号）, 广州联通电路编号, 备注 from fh300_port.750") 

	for row in g.cursor.fetchall():	#row是一个列值的tuple。((A1,B1,C1),(A2,B2,C2),(A3,B3,C3))
		data = dict(zip(field_names, row))
		datas.append(data)
	return json.dumps(datas)


@otn.route('/update', methods=['POST'])	#更新表格内容
def update():
	datas = []
	#fields_doct = {"no":u"序号","anode":u"站点（本端落地）","direction":u"方向","znode":u"对端落地","route":"波道路由","wavelength"u"对应的高端系统时隙编号（波长编号）","index":u"广州联通电路编号","remark":u"备注"}
	field_names = ["vender","tablename","anode","direction","znode","route","wavelength","index","remark","no"]
	field_names_ = ["no","anode","direction","znode","route","wavelength","index","remark"]
	values = map(lambda x:request.form[x], field_names)

	sql = u"update %s.%s set 站点（本端落地）='%s',方向='%s',对端落地='%s',波道路由='%s',对应的高端系统时隙编号（波长编号）='%s',广州联通电路编号='%s',备注='%s' where 序号=%s" % tuple(values)
	g.cursor.execute(sql)	#得提交commit
	g.conn.commit()
	
	return sql 	#可以返回参数