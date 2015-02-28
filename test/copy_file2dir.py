# -*- coding:utf8 -*-
"""
TODO:
    得先确保能连接上"\\10.117.193.234\资源调度",通过调用bat命令来实现？
导入ini配置文件，复制excel文件到指定的文件夹
"""
import os, sys
import shutil
import manage_config
import subprocess       #导入这个模块运行系统命令


"""
首先，确保连接到\\10.117.193.234\资源调度

returncode = subprocess.call('net use \\10.117.193.234\资源调度 "zydd-8888" /user:"user"',shell=True)
print returncode
if returncode != 0:
    sys.exit(1)
"""

config_file = os.path.join(os.path.dirname(__file__), 'excel_path.ini')
a = manage_config.Config(config_file)

excel_path = [
                    r"\\10.117.193.234\资源调度\传输\SDH客户路由台账\客户电路1(融合资源).xlsx",
                    r"\\10.117.193.234\资源调度\传输\移动网台帐(最新)\通路组织表\2G台帐\基站通路组织表(最新).xlsm",
                    r"\\10.117.193.234\资源调度\传输\移动网台帐(最新)\通路组织表\3G台帐\3G基站电路台帐(最新).xlsm",
                    r"\\10.117.193.234\资源调度\传输\调度\备份\最新备份\烽火电路台账20130327.xlsx",
                    r"\\10.117.193.234\资源调度\传输\移动网台帐(最新)\烽火IPRAN基础维护资料\烽火IPRAN业务台账.xlsm",
                    r"\\10.117.193.234\资源调度\传输\移动网台帐(最新)\通路组织表\本地网通路组织表\本地网通路组织表（不包含客户电路、最新）.xlsx",
                    r"\\10.117.193.234\资源调度\传输\移动网台帐(最新)\通路组织表\长途台帐\长途数据库（最新）.xls",
                    r"\\10.117.193.234\资源调度\传输\移动网台帐(最新)\华为IPRAN基础维护资料\IPRAN业务台账.xlsm",
                    r"\\10.117.193.234\资源调度\传输\OTN业务台账\波分业务路由表（最新）.xlsx",
                    r"\\10.117.193.234\资源调度\传输\移动网台帐(最新)\通路组织表\C网台帐\C网路由(最新).xls",
                    r"\\10.117.193.234\资源调度\传输\固网台帐\传输台帐\传输公文包\开通汇总表\城域传输路由台帐\客户电路1(融合资源).xlsx",
                    r"\\10.117.193.234\资源调度\传输\固网台帐\传输台帐\传输公文包\开通汇总表\城域传输路由台帐\客户电路2(移网).xlsx",
                    r"\\10.117.193.234\资源调度\传输\SDH客户路由台账\客户电路2(移网).xlsx",
                    ]
field = "import_file"

for i in range(len(excel_path)):
    key = "file%d" % (i+1)
    value = excel_path[i]
    a.set(field, key, value)

a.remove_section(field)   #删除section
a.write()
"""
src = r'C:\传输值班台账汇总\3G基站电路台帐(最新).xlsm'.decode('utf8')
dst_dir = r"D:\\".decode('utf8')
shutil.copy(src, dst_dir)
"""