#-*-coding:utf8-*-

a_out = open(r"C:\Users\devilman\Desktop\a_out.txt","r")
b_out = open(r"C:\Users\devilman\Desktop\b_out.txt","r")

a_content = a_out.read()
b_list = b_out.readlines()

c_out = open(r"C:\Users\devilman\Desktop\c_out.txt","w")
c_list = []
for b in b_list:
    if a_content.find(b)>=0:
        c_list.append(b)

c_out.writelines(c_list)

a_out.close()
b_out.close()
c_out.close()