# -*- coding:utf-8 -*-
__author__ = 'lightsing'

class Command(object) :
    def __init__(self, contents = ['',], type = '') :
        if type :
            self.type = type
            self.data = ','.join(contents.insert(0,str(type)))
        else :
            self.type = contents[0]
            self.data = ','.join(contents)
            contents.pop(0)
        self.contents = contents
    def rebuild(str) :
        contents = str.split(',')
        return Command(contents)
