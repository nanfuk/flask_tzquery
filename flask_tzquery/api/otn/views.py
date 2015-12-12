#-*-coding:utf8-*-
import sys
import xlrd, xlwt
from flask import g, request, jsonify, json, abort, current_app
import pdb
import MySQLdb
#from config import vender_file_dict, tablename_dict

#sys.path.append("..")   #是为了使用上级目录的模块

#otn = Blueprint("otn", __name__)
from . import bp
from ... import excel_engine    #excel_engine模块在上两级目录。


class data_strucure():      #数据结构
    def __init__(self, table, table_row):
        #table = data.sheet_by_name(table_name)
        self.jf = table.cell(table_row, 1).value    #B列，机房名
        self.jjh = table.cell(table_row, 8).value       #I列，机架号
        self.jkh = str(table.cell(table_row, 9).value).rstrip(".0")     #J列，机框号，数字
        self.cwh = str(table.cell(table_row, 10).value).rstrip(".0")    #K列，槽位号，数字
        self.dbm = table.cell(table_row, 11).value  #L列，单板名
        self.dkh = str(table.cell(table_row, 12).value).rstrip(".0")    #M列，端口号，数字
        self.odf = table.cell(table_row, 15).value  #P列，ODF架位
        self.bd = table.cell(table_row, 6).value        #G列，波道
        self.lyxx = table.cell(table_row, 4).value  #E列，环路路由信息

@bp.before_app_first_request
def test():
    current_app.config['xlsApp'] = excel_engine.init() #初始化。放在第一次请求前，是为了防止debug为true时两次加载造成启动两个excel进程的问题。
    #print excel.xlsApp
    #current_app.config['xlsApp'] = excel.xlsApp   #把启动的excel存入application context中，可以给其它函数调用。

@bp.before_request
def before_request():
    try:
        vender = request.form['vender']
        #
        if vender=="hw":
            #workbook_path = r"D:\flask_env\波分端口台账\华为波分端口资源表格（最新）.xls".decode("utf8")  #相对路径
            workbook_path = current_app.config['VENDER_FILE_DICT']["hw_port"]
        elif vender=="fh3000":
            #workbook_path = r"..\波分端口台账\烽火波分3000端口资源表格（最新）.xlsx".decode("utf8")
            workbook_path = current_app.config['VENDER_FILE_DICT']["fh300_port"]
        elif vender=="fh4000":
            workbook_path = current_app.config['VENDER_FILE_DICT']["fh4000_port"]
        elif vender=="zx":
            workbook_path = current_app.config['VENDER_FILE_DICT']["zx_port"]    
        g.wb = xlrd.open_workbook(workbook_path)

    except:
        username = current_app.config['USER']
        passwd = current_app.config['PWD']
        g.conn = MySQLdb.connect(host="127.0.0.1",user=username,passwd=passwd,charset='gbk') 
        g.cursor = g.conn.cursor()

@bp.teardown_request   #是当request的context被弹出时，自动调用的函数。这里是关闭数据库。
def teardown_request(exception):
    #pdb.set_trace()
    wb = getattr(g, 'wb', None)
    conn = getattr(g, 'conn', None)
    ws = getattr(g, 'ws', None)
    if wb is not None:
        #wb.close()     #待分析是否这样关闭
        pass
    if conn is not None:
        conn.close()
    if ws is not None:
        xlsApp = current_app.config['xlsApp']
        xlsApp.close(True)
        
@bp.route('/get_tree_json')
def tree():
    tablename_dict = {'750':u'750','baiyunting':u'白云厅','danan':u'大南', 'gangqian':u'岗前','guiguan':u'桂冠','gyy':u'工业园','haijingcheng':u"海景城","hebinnan":u"河滨南","hetai":u"和泰",
    "huaduguangdian":u"花都广电",'jinzhou':u'金州',"kxc":u"科学城","qs":u"七所",'shiji':u"石基",'tyc':u"太阳城",'xinganglou':u"新港楼",'xm':u"夏茅",
    "xsk":u"新时空","yj":u"云景","kexuezhongxinbei":u"科学中心北","changgangzhong":u"昌岗中","dongpushangye":u"东圃商业","dongxing":u"东兴","hualong":u"化龙","jiayi":u"加怡",
    "nanguohuayuan":u"南国花园","nantianguangchang":u"南天广场","yuandong":u"远东","yuehao":u"越豪","zhongqiao":u"中侨","zhujiangguangchang":u"珠江广场","yuntai":u"蕴泰"}
    list_data = []

    vender_db_list = [('fh300_port',u"烽火3000"),('hw_port',u"华为"),('fh4000_port',u"烽火4000"),('zx_port',u"中兴")]

    for vender_db,vender_name in vender_db_list:
        dict_data = {}
        dict_data.setdefault("id",vender_db)    #使用字典的setdefault来添加项值对
        dict_data.setdefault("text",vender_name)    #字典取值
        g.cursor.execute("select table_name from information_schema.tables where table_schema='%s'" % vender_db)
        for tablename in g.cursor.fetchall():   #这里是添加列表，并配合列表的append来增长列表，可以看笔记记录的字典操作
            dict_data.setdefault("children",[]).append({"text":tablename_dict[tablename[0]], "id":tablename[0],"attributes":{"parent":"%s" % vender_db}})
            #为了能得到combotree选取值的父节点，加了attributes属性，使用方法:node.attributes.parent
    
        list_data.append(dict_data)

    return json.dumps(list_data)


@bp.route('/dispatch', methods=['POST'])
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


@bp.route('/port', methods=['GET','POST'])
def otn_port():
    datas = []
    field_names = ["no","anode","direction","znode","route","wavelength","neident","port","index","remark"]
    if request.method=='GET':
        dbname = request.args.get('vender_otn', '')
        tablename = request.args.get('jf_name', '')
        #wavelength = request.args.get('wavelength_val', "")

        g.cursor.execute(u"select 序号, 站点（本端落地）, 方向, 对端落地, 波道路由, 对应的高端系统时隙编号（波长编号）, 机架编号, 槽号, 广州联通电路编号, 备注 from %s.%s" % (dbname,tablename)) 
        """
        if wavelength !="":
            g.cursor.execute(u"select 序号, 站点（本端落地）, 方向, 对端落地, 波道路由, 对应的高端系统时隙编号（波长编号）, 机架编号, 槽号, 广州联通电路编号, 备注 from %s.%s where 对应的高端系统时隙编号（波长编号） like '_%s%%'" % (dbname,tablename,wavelength)) 
        else:
            g.cursor.execute(u"select 序号, 站点（本端落地）, 方向, 对端落地, 波道路由, 对应的高端系统时隙编号（波长编号）, 机架编号, 槽号, 广州联通电路编号, 备注 from %s.%s" % (dbname,tablename)) 
        """
    else:
        g.cursor.execute(u"select 序号, 站点（本端落地）, 方向, 对端落地, 波道路由, 对应的高端系统时隙编号（波长编号）, 机架编号, 槽号, 广州联通电路编号, 备注 from fh300_port.750") 
        
    for row in g.cursor.fetchall(): #row是一个列值的tuple。((A1,B1,C1),(A2,B2,C2),(A3,B3,C3))
        data = dict(zip(field_names, row))
        datas.append(data)
    return json.dumps(datas)


@bp.route('/update', methods=['POST']) #更新表格内容
def update():
    field_names = ["vender","tablename","anode","direction","znode","route","wavelength","index","remark","no"]
    values = map(lambda x:request.form[x], field_names)
    excelName = current_app.config['VENDER_FILE_DICT'][request.form["vender"]] #得excel名
    #excelName = vender_file_dict[request.form["vender"]]    #得excel名
    #sheet = tablename_dict[request.form["tablename"]]   #得表名
    sheet = current_app.config['TABLENAME_DICT'][request.form["tablename"]]   #得表名
    row_index = int(request.form["no"])    #得行号，强制转为int类型，得加1才行
    index = request.form["index"]       #电路编号
    remark = request.form["remark"]     #备注

    sql = u"update %s.%s set 站点（本端落地）='%s',方向='%s',对端落地='%s',波道路由='%s',对应的高端系统时隙编号（波长编号）='%s',广州联通电路编号='%s',备注='%s' where 序号=%s" % tuple(values)
    try:
        #pdb.set_trace()
        g.cursor.execute(sql)   #得提交commit
        g.conn.commit()
        #存入excel
        xlsApp = current_app.config['xlsApp']
        #pdb.set_trace()
        g.ws = xlsApp.open(excelName, sheet, isDisplay=False)
        xlsApp.write(row_index+1, 15, index)   #15列为电路编号，17列为备注
        xlsApp.write(row_index+1, 18, remark)   #18列为备注
        #g.ws = excel.open(excelName, sheet, isDisplay=False)
        #pdb.set_trace()
        
    except:
        #pass
        abort(501)  #更新失败则返回错误代码
    return sql  #可以返回参数