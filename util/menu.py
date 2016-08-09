# -*- coding:utf-8 -*-
__author__ = 'lightsing'

class Menu(object) :
    def __init__(self, contents, title = '') :
        self.__title = title
        self.__contents = contents

    def printMenu(self):
        if self.__title :
            print(self.__title)
        length = range(len(self.__contents))
        for index in length :
            print('%d.%s' % (index+1, self.__contents[index]))

        finish = False
        while not finish :
            try:
                choice = int(input('Enter a number to continue: '))
                if choice-1 in length :
                    finish = True
                    return choice
                else :
                    print('Out of range.\nTry Again.')
            except:
                print('Cannot Accept Non-number Input.\nTry Again.')
