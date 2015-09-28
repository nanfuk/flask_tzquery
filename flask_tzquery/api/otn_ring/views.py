#-*-coding:utf8-*-
from flask import g, request
import MySQLdb    
import pdb,json

from . import bp


#otn_ring = Blueprint("otn_ring", __name__)

@bp.before_request      #表示在请求页面之前先连接好数据库
def before_request():
	g.conn = MySQLdb.connect(host="127.0.0.1",user="root",passwd="lanbinbin1989",db="test", charset='gbk')  
	g.cursor = g.conn.cursor()

@bp.teardown_request   #是当request的context被弹出时，自动调用的函数。这里是关闭数据库。
def teardown_request(exception):
    conn = getattr(g, 'conn', None)
    if conn is not None:
        conn.close()


@bp.route('/get_data', methods=['POST'])
def get_data():

	vender = request.form['vender']		#这是得到POST参数的方法
	#area = request.args.get('area', '')	#这是得到GET参数的方法

	#print u'厂家：%s' % vender

	field_names = ["ring_index", "equiptype", "node", "remark"]
	datas = []

	g.cursor.execute(u"select 环路编号, 类型, 环上节点,备注 from %s" % vender)   	#待改，不需要获取这么多的数据

	for row in g.cursor.fetchall():	#row是一个列值的tuple。((A1,B1,C1),(A2,B2,C2),(A3,B3,C3))
		data = dict(zip(field_names, row))
		datas.append(data)
	 
	return json.dumps(datas)


    	
        	