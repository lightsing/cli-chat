# -*- coding:utf-8 -*-
__author__ = 'lightsing'

import re

import socket
from getpass import getpass
from Crypto.Hash import SHA256
from util.crypto import Operator as crypto
from util.command import Command
from util import myprint as print
from util.client import mainMenu
from util import __addr__

class User(object) :
    def __init__(self) :
        self.__username = ''
        self.__password = ''
        self.__rsa = crypto(remote = 'server-public.pem', opt_len = 1024)
        self.online = False
        self.token = ''
        if mainMenu.printMenu() != 1 :
            exit()
        try :
            attemps = 3
            while attemps > 0 :
                self.setUsername()
                self.setPassword()
                self.online = self.login()
                if self.online :
                    break
                attemps -= 1
                print('\nLogin Faild, remain attemps %d.' % attemps, color = 'r')
        except :
            print('Initialize Faild.\nCannot connet to server.', color = 'r')
            raise
            exit(-1)

    def setUsername(self) :
        log_finish = False
        while not log_finish :
            username = input('\nShow me your identity:')
            if not re.match(r'[a-zA-Z][0-9a-zA-Z]*', username) :
                print('\nInvaild identity, Please try again.', color = 'r')
                continue
            confirm = input('\nYou will log in as [%s].\nAre you sure?[Y/N/(C)ancel]:' % username)
            if confirm in ['Y','y'] :
                log_finish = True
                self.__username = username
            elif confirm in ['Cancel','C','c'] :
                exit()

    def setPassword(self) :
        log_finish = False
        while not log_finish :
            password = getpass('\nShow me your password:')
            repassword = getpass('Retype your password:')
            if password == repassword :
                log_finish = True
                self.__password = SHA256.new(password.encode('utf-8')).hexdigest()

    def login(self) :
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(__addr__)
        crypto.sendEncrypted(conn,Command(['login',self.__username,self.__password,self.__rsa.pub.exportKey().decode('utf-8')]).data,self.__rsa.remote)
        response = crypto.recvWithSign(conn, self.__rsa.remote)
        if response == 'Success' :
            token = crypto.recvDecrypted(conn, self.__rsa.sec)
            print('Log in successfully')
            self.token = token
            conn.close()
            return True
        else :
            print('Error: %s' % response, color = 'r')
            conn.close()
            return False
