#-*-coding:utf8-*-

def preKey(str):      #对关键字进行预处理
    str = str.strip()
    pattern = re.compile("%")
    str = pattern.sub("%%", str)
    pattern = re.compile(r"\[")   #①r表示字符串的'\'不需转义。②但'['不能直接compile，需要'\'转义才能compile
    str = pattern.sub("%[", str)
    return str.split('*')   #返回的是一个列表