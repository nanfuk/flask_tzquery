# -*- coding:utf8 -*-
"""
操作ini配置文件的模块
使用步骤：

ini文件的格式：
注解使用分号表示（;）。在分号后面的文字，直到该行结尾都全部为注解。
; comment textINI文件的数据格式的例子（配置文件的内容）　    #这是ini文件的注释
[Section1 Name]
KeyName1=value1
KeyName2=value2
...
[Section2 Name]
KeyName21=value21
KeyName22=value22
"""
import sys
import ConfigParser
import pdb

class Config:
    def __init__(self, path):
        self.path = path
        self.cf = ConfigParser.ConfigParser()
        try:
            #pdb.set_trace()
            self.cf.read(self.path)      
            #得特别注意用笔记本修改配置文档后，Windows会默认添加EF BB BF三个字节
            #触发MissingSectionHeaderError异常。所以得进行异常处理。
        except ConfigParser.MissingSectionHeaderError:
            
            a = open(self.path, 'rb')      #这一段是为了去掉那三个字节，有点拖沓。应该可以优化-。-
            tmp = a.read()
            a.close()
            b = open(self.path, 'wb')
            b.write(tmp[3:])
            b.close()

            self.cf.read(self.path)   #这里参数只能是文件路径，或者是文件路径列表

    def get(self, field, key):
        result = ""
        try:
            result = self.cf.get(field, key)
        except:
            result = ""
        return result

    def set(self, field, key, value):
        try:
            self.cf.set(field, key, value)
        except ConfigParser.NoSectionError:
            self.cf.add_section(field) 
            self.cf.set(field, key, value)

    def write(self):   #set,remove_section运行完后再写入文件。！
        self.cf.write(open(self.path, 'w'))    #这就是写ini的格式，已字节方式写入才不会出错

    def remove_section(self, section):
        self.cf.remove_section(section)

    def get_sections(self):
        return self.cf.sections()

    def get_keys(self, section):
        return self.cf.options(section)



def read_config(config_file_path, field, key):
    cf = ConfigParser.ConfigParser()
    try:
        cf.read(config_file_path)
        result = cf.get(field, key)
    except:
        sys.exit(1)
    return result

def write_config(config_file_path, field, key, value):
    cf = ConfigParser.ConfigParser()
    try:
        cf.read(config_file_path)
        cf.set(field, key, value)
        cf.write(open(config_file_path, 'w'))
    except:
        sys.exit(1)
    return True


if __name__ == "__main__":
    if len(sys.argv)<4:   
        #命令是python ini_base.py file_path field, key, value，所以有5个参数。
        #只有四个的话，为读。五个，为写。
        sys.exit(1)

    config_file_path = sys.argv[1]
    field = sys.argv[2]
    key = sys.argv[3]
    if len(sys.argv) == 4:
        print read_config(config_file_path, field, key)
    else:
        value = sys.argv[4]
        write_config(config_file_path, field, key, vlaue)