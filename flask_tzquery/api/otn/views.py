#-*-coding:utf8-*-
import sys, time
import xlrd, xlwt
from xlutils.copy import copy
from flask import g, request, jsonify, json, abort, current_app, make_response

 


import MySQLdb
import StringIO, re
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
    #current_app.config['xlsApp'] = excel_engine.init() #初始化。放在第一次请求前，是为了防止debug为true时两次加载造成启动两个excel进程的问题。
    pass
    #print excel.xlsApp
    #current_app.config['xlsApp'] = excel.xlsApp   #把启动的excel存入application context中，可以给其它函数调用。

@bp.before_request
def before_request():
    try:
        vender = request.form['vender']
        if vender in ["hw_port","zx_port","fh3000_port","fh4000_port"]:
            workbook_path = current_app.config['VENDER_FILE_DICT'][vender]
            g.wb = xlrd.open_workbook(workbook_path)
        else:
            pass

    except:
        username = current_app.config['USER']
        passwd = current_app.config['PWD']
        g.conn = MySQLdb.connect(host="127.0.0.1",user=username,passwd=passwd,charset='utf8') 
        g.cursor = g.conn.cursor()

@bp.teardown_request   #是当request的context被弹出时，自动调用的函数。这里是关闭数据库。
def teardown_request(exception):
    wb = getattr(g, 'wb', None)
    conn = getattr(g, 'conn', None)
    ws = getattr(g, 'ws', None)
    xlsApp = getattr(g, 'xlsApp', None)

    if wb is not None:
        #wb.close()     #待分析是否这样关闭
        pass
    if conn is not None:
        conn.close()
    if ws is not None:
        xlsApp = current_app.config['xlsApp']
        xlsApp.close(True)
        
    if xlsApp is not None:
        xlsApp.close(isSave=True)   #保存并关闭wb
        #xlsApp.app_quit()   #退出并销毁进程
        
@bp.route('/get_tree_json')
def tree():
    tablename_dict = {'750':u'750','baiyunting':u'白云厅','danan':u'大南', 'gangqian':u'岗前','guiguan':u'桂冠','gyy':u'工业园','haijingcheng':u"海景城","hebinnan":u"河滨南","hetai":u"和泰",
    "huaduguangdian":u"花都广电",'jinzhou':u'金州',"kxc":u"科学城","qs":u"七所",'shiji':u"石基",'tyc':u"太阳城",'xinganglou':u"新港楼",'xm':u"夏茅",
    "xsk":u"新时空","yj":u"云景","kexuezhongxinbei":u"科学中心北","changgangzhong":u"昌岗中","dongpushangye":u"东圃商业","dongxing":u"东兴","hualong":u"化龙","jiayi":u"加怡",
    "nanguohuayuan":u"南国花园","nantianguangchang":u"南天广场","yuandong":u"远东","yuehao":u"越豪","zhongqiao":u"中侨","zhujiangguangchang":u"珠江广场","yuntai":u"蕴泰","jinfa":u"金发"}
    list_data = []

    vender_db_list = [('fh3000_port',u"烽火3000"),('hw_port',u"华为"),('fh4000_port',u"烽火4000"),('zx_port',u"中兴")]

    for vender_db,vender_name in vender_db_list:
        dict_data = {}
        dict_data.setdefault("id",vender_db)    #使用字典的setdefault来添加项值对
        dict_data.setdefault("text",vender_name)    #字典取值
        g.cursor.execute("select table_name from information_schema.tables where table_schema='%s'" % vender_db)
        for tablename in g.cursor.fetchall():   #这里是添加列表，并配合列表的append来增长列表，可以看笔记记录的字典操作
            dict_data.setdefault("children",[]).append({"text":tablename_dict[tablename[0]], "id":tablename[0],"attributes":{"parent":vender_db,"parentname":vender_name}})
            #为了能得到combotree选取值的父节点，加了attributes属性，使用方法:node.attributes.parent
    
        list_data.append(dict_data)

    return json.dumps(list_data)


@bp.route('/dispatch', methods=['POST'])
def dispatch():
    source_table_name = request.form['atable']
    source_table_row = int(request.form['ano'])
    dest_table_name = request.form['ztable']
    dest_table_row = int(request.form['zno'])

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
    return route


# @bp.route('/port', methods=['GET','POST'])
@bp.route('/port', methods=['GET'])
def otn_port():
    datas = []
    field_names = [ "no","anode","direction","znode","route","system","wavelength","neident","jijiano",
                    "kuangno","port","boardname","portindex","linetype","index","odf","rtx",
                    "remark","lineport"]   #顺序不能乱
    dbname = request.args.get('vender_otn', '')
    tablename = request.args.get('jf_name', '')
    sql = u"""
        select  序号, 
                站点（本端落地）,
                方向,
                对端落地,
                波道路由,
                所属系统,
                对应的高端系统时隙编号（波长编号）,
                网元标识,
                机架编号,
                框编号,
                槽号,
                单板名称,
                端口编号,
                电路类型,
                广州联通电路编号,
                `端子号（DDF/ODF架号-子模块号-端子号）`,
                `收/发`,
                备注,
                对应10G波长转换板
        from %s.%s""" % (dbname,tablename)

    try:
        g.cursor.execute(sql)
    except Exception,e:
        # pdb.set_trace()
        print e
        abort(400)
       
    for row in g.cursor.fetchall(): #row是一个列值的tuple。((A1,B1,C1),(A2,B2,C2),(A3,B3,C3))
        data = dict(zip(field_names, row))
        datas.append(data)
    return json.dumps(datas)


@bp.route('/export_dispatch_excel', methods=["POST"])
def export_dispatch_excel():
    rowindex = 1
    content = json.loads(request.form["content"])
    ISOTIMEFORMAT = "%y-%m-%d-%H_%M_%S"
    lt = time.localtime()
    ft = time.strftime(ISOTIMEFORMAT, lt)

    file_path = current_app.config['DISPATCH_TEMPLATE']
    rb = xlrd.open_workbook(file_path, formatting_info=True)
    w = copy(rb)
    wb = w.get_sheet(0)

    for row in content:
        for columnindex,data in enumerate(row):
            wb.write(rowindex, columnindex, data)
        rowindex += 1

    sio = StringIO.StringIO()
    w.save(sio)

    rsp = make_response(sio.getvalue(),200)
    rsp.headers["Content-type"] = "application/vnd.ms-excel"
    rsp.headers["Transfer-Encoding"] = "chunked"
    rsp.headers["Content-Disposition"] = "attachment;filename='%s.xls'" % ft
    return rsp


# 更新端口表格内容，包括excel
@bp.route('/update', methods=['POST'])
def update():
    action = request.form["action"]
    updatedata = json.loads(request.form["updatedata"])
    
    for data in updatedata:
        db = data["vender"]
        tablename = data["tablename"]
        efile = current_app.config['VENDER_FILE_DICT'][db] #得excel名
        sheet = current_app.config['TABLENAME_DICT'][tablename]   #得表名
        rows = data["rows"]
        updatedb(db, tablename, rows)
        updateexcel(efile, sheet, rows)
    
    return "success"  #可以返回参数


# 更新数据库
def updatedb(db, tablename, rows):
    field_names = [ "anode","direction","znode","route","system","wavelength","neident","jijiano",
                    "kuangno","port","boardname","portindex","linetype","index","odf","rtx",
                    "remark","lineport"]   #顺序不能乱
    for row in rows:
        values = map(lambda x:row[x], field_names)
        values.append(row["no"])
        values.insert(0, tablename)
        values.insert(0, db)
        sql =  u"""
                update %s.%s
                set 站点（本端落地）='%s',
                    方向='%s',
                    对端落地='%s',
                    波道路由='%s',
                    所属系统='%s',
                    对应的高端系统时隙编号（波长编号）='%s',
                    网元标识='%s',
                    机架编号='%s',
                    框编号='%s',
                    槽号='%s',
                    单板名称='%s',
                    端口编号='%s',
                    电路类型='%s',
                    广州联通电路编号='%s',
                    `端子号（DDF/ODF架号-子模块号-端子号）`='%s',
                    `收/发`='%s',
                    备注='%s',
                    对应10G波长转换板='%s'
                where 序号=%s""" % tuple(values)
        g.cursor.execute(sql)
    g.conn.commit()

# 更新excel
def updateexcel(efile, sheet, rows):
    field_names = [ "anode","direction","znode","route","system","wavelength","neident","jijiano",
                    "kuangno","port","boardname","portindex","linetype","index","odf","rtx",
                    "remark","lineport"]   #顺序不能乱
    xlsApp = excel_engine.init()
    xlsApp.open(efile, sheet, isDisplay=False)
    for row in rows:    #再来个循环，更新xls数据
        values = map(lambda x:row[x], field_names)  #逐行更新
        row_index = row["no"]
        for i,value in enumerate(values):   #从第二列开始更新
            xlsApp.write(row_index+1, i+2, value)
    xlsApp.close(isSave=True)   #保存并关闭wb

