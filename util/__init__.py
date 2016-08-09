# -*- coding:utf-8 -*-
__author__ = 'lightsing'

__port__ = 9999
__addr__ = ('127.0.0.1', __port__)

__version__ = 0.1

def myprint(mes, color = 'default'):
    if color == 'r':
        fore = 31
    elif color == 'g':
        fore = 32
    elif color == 'b':
        fore = 36
    elif color == 'y':
        fore = 33
    else:
        fore = 37
    color = "\x1B[%d;%dm" % (1,fore)
    print("%s%s\x1B[0m" % (color,mes))
