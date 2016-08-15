# -*- coding:utf-8 -*-
__author__ = 'lightsing'

import re

import socket, base64
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
        self.unread = []
        self.switchHeader = []
        self.switch = {
        'find': self.switchFind,
        #'send': self.switchSend,
        #'sendDirect': self.switchSendDirect,
        #'getUnread': self.switchGetUnread,
        }
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
        self.keepOnline()
        self.find('ty')
        self.logout()


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
            conn.close()
            print('Log in successfully')
            self.token = token
            self.switchHeader = [self.__username,self.token]
            return True
        else :
            print('Error: %s' % response, color = 'r')
            conn.close()
            return False

    def logout(self) :
        if self.online :
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect(__addr__)
            crypto.sendEncrypted(conn,Command(['logout',self.__username,self.token]).data,self.__rsa.remote)
            response = crypto.recvWithSign(conn, self.__rsa.remote)
            conn.close()
        #print(response)

    def keepOnline(self) :
        if self.online :
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect(__addr__)
            crypto.sendEncrypted(conn,Command(['online',self.__username,self.token]).data,self.__rsa.remote)
            response = crypto.recvWithSign(conn, self.__rsa.remote)
            conn.close()
        print(response)

    def switchHandler(self, action, data) :
        if self.online :
            message = self.switchHeader + [action,data]
            message.insert(0,'switch')
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect(__addr__)
            crypto.sendEncrypted(conn,Command(message).data,self.__rsa.remote)
            response = crypto.recvWithSign(conn, self.__rsa.remote)
            if response == 'Accepted' :
                #response = crypto.recvDecrypted(conn, self.__rsa.sec)
                self.switch[action](conn)
                conn.close()
                return response
            else :
                print('Error: %s' % response, color='r')
                conn.close()

    def switchFind(self, conn) :
        #data = crypto.recvDecryptedAES(conn, self.token)
        raw = conn.recv(10240)
        raw = base64.b64decode(raw)
        print(len(raw))
        data = crypto.decryptAES(raw, self.token)

        if data :
            response = crypto.decryptAES(data,self.token)
            print(response)
        else :
            print('No response in find request', color='r')
            conn.close()

    def find(self, username) :
        if self.online :
            query = self.switchHandler('find', crypto.encryptAES(username, self.token).decode('utf-8'))
            print(query)
