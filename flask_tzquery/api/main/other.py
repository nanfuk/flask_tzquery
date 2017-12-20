#-*-coding:utf8-*-
import re

def preKey(strList):      #对关键字进行预处理
    p = re.compile(r"[\]\[\%]")     #用于转义[,],%这些access混淆的符号
    return [p.sub(lambda m:"[%s]" % m.group(), str.strip()) for str in strList]

def resumeKey(strList):     #对关键字进行还原
    p = re.compile(r"\[(.*?)\]")    #把[[]，[%]，[]]还原为[, ], %
    return [p.sub(lambda m:m.group(1),str) for str in strList]
