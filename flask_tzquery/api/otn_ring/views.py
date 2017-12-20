#-*-coding:utf8-*-
from flask import g, request, current_app
import MySQLdb 
import json, logging, re
from . import bp

logger = logging.getLogger("otn_ring")
#otn_ring = Blueprint("otn_ring", __name__)

@bp.before_request      #表示在请求页面之前先连接好数据库
def before_request():
    username = current_app.config['USER']
    passwd = current_app.config['PWD']
    g.conn = MySQLdb.connect(host="127.0.0.1",user=username,passwd=passwd,db="test", charset='utf8')
    g.cursor = g.conn.cursor()

@bp.teardown_request   #是当request的context被弹出时，自动调用的函数。这里是关闭数据库。
def teardown_request(exception):
    conn = getattr(g, 'conn', None)
    if conn is not None:
        conn.close()


@bp.route('/get_data', methods=['POST'])
def get_data():

    vender = request.form['vender']     #这是得到POST参数的方法
    #area = request.args.get('area', '')    #这是得到GET参数的方法

    #print u'厂家：%s' % vender

    field_names = ["ring_index", "equiptype", "node", "remark"]
    datas = []

    g.cursor.execute(u"select 环路编号, 类型, 环上节点,备注 from %s" % vender)      #待改，不需要获取这么多的数据

    for row in g.cursor.fetchall(): #row是一个列值的tuple。((A1,B1,C1),(A2,B2,C2),(A3,B3,C3))
        data = dict(zip(field_names, row))
        datas.append(data)
     
    return json.dumps(datas)


@bp.route('/getWaves', methods=['POST'])
def getWaves():
    # import pdb;pdb.set_trace()
    field_names = ["index", "link", "nums", "content"]
    datas = []

    ring = request.form["ring_index"]
    nodes = request.form["nodes"]
    pattern = re.compile(r"-+")
    nodes = pattern.split(nodes.strip())    # 去除nodes两端的空格
    for i in range(len(nodes)-1):
        content = filterWave(ring.strip(), nodes[i], nodes[i+1])    # 去除ring两端的空格
        data = dict(zip(field_names, [i+1,nodes[i]+'---'+nodes[i+1], len(content), content]))
        # print len(content)
        datas.append(data)
    return json.dumps(datas)


def filterWave(ring, Apoint, Zpoint):
    # conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="1989", port=3306, charset="utf8")
    conn = g.conn
    cur  = g.cursor

    field_names = ["route","wl"]
    datas = []

    if ring[0:3] == "FWR":
        if int(ring[3:]) in (9,14,15,16):
            table_schema = 'fh4000_port'
        else:
            table_schema = 'fh3000_port'
    elif ring[0:3] == "HWR":
        table_schema = 'hw_port'
    elif ring[0:3] == "ZWR":
        table_schema = 'zx_port'
    else:
        raise ValueError, u"输入的环路名称有误！".encode("GBK")

    conn.select_db(table_schema)
    cur.execute("select table_name from information_schema.tables where table_schema='%s'" % table_schema)

    sql = ""
    for i in cur.fetchall():
        table_name = "`%s`" % i[0]  #预防750类似字样无法作为表名，需要加反引号
        sql1 = u"select 波道路由,对应的高端系统时隙编号（波长编号） from %s" % table_name
        if sql == "":
            sql = sql1
        else:
            sql += " union "+sql1
    # 使用的是union，不是union all，相同的项会被剔除

    AtoZ = Apoint+"-"+Zpoint
    ZtoA = Zpoint+"-"+Apoint

    # sql = u"select 波道路由,对应的高端系统时隙编号（波长编号） from (%s) as T1 where 波道路由 like '%%%s%%' and 对应的高端系统时隙编号（波长编号） like '%%%s%%'" % (sql,u"750-新时空",u"λ8")

    sql = u"select 波道路由,对应的高端系统时隙编号（波长编号） from (%s) as T1 where 波道路由 like '%%%s%%' or  波道路由 like '%%%s%%'" % (sql,AtoZ,ZtoA)

    sql = sql.encode("utf8")

    cur.execute(sql)

    output = cur.fetchall()

    wlList = []
    # wlRouteDict = dict()

    pattern1 = re.compile(u".*%s[\(（](.+?)[\)）].*" % ring)
    pattern2 = re.compile(u".*[λ入](\d+).*")  
    for i in output:    #i[0]代表的是路由信息，i[1]代表的是波长编号
        match1 = pattern1.match(i[0])
        if match1 and i[1]:
            if match1.group(1).find(AtoZ)>=0 or match1.group(1).find(ZtoA)>=0:
                match2 = pattern2.match(i[1])
                if match2:
                    wl = int(match2.group(1))
                    if wl not in wlList:
                        # routeList.append(i[0])
                        wlList.append(wl)
                        data = dict(zip(field_names, [i[0],wl]))
                        datas.append(data)
                        # wlRouteDict[wl] = i[0]
        else:
            logger.warn(u"%s-%s与%s不匹配 %s %s", Apoint, Zpoint, ring, i[0], i[1])

    return datas
            