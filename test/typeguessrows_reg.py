# -*- coding:utf8 -*-
"""
修改注册表，来更改excel的导入时的预读行数，从而让程序正确的判断字段类型。
"""
import _winreg
import platform
#import win32con

win_ver = platform.uname()[4]
if win_ver=="x86":
    #key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Office\12.0\Access Connectivity Engine\Engines\Excel')
    key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Office\12.0\Access Connectivity Engine\Engines\Excel',
                                            0, _winreg.KEY_ALL_ACCESS)
    #必须修改访问权限，才能修改注册表。默认是只读的。通过_winreg.KEY_ALL_ACCESS来修改。
    _winreg.SetValueEx(key, "TypeGuessRows", 0,  _winreg.REG_DWORD, 0)
    #value,type = _winreg.QueryValueEx(key, "TypeGuessRows")
    #print value,type
    #print _winreg.REG_DWORD

elif win_ver=="AMD64":
    key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Wow6432Node\Microsoft\Office\12.0\Access Connectivity Engine\Engines\Excel',
                                            0, _winreg.KEY_ALL_ACCESS)
    _winreg.SetValueEx(key, "TypeGuessRows", 0,  _winreg.REG_DWORD, 0)

else:
    print u'未支持的系统！'