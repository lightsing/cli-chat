# -*- coding:utf-8 -*-
import socket, threading, time, sqlite3
from util.crypto import Operator as crypto
from Crypto.PublicKey import RSA
from util.command import Command
from util.user import User
from util import myprint as print
from util import __version__, __addr__, __port__
class Processor(object) :
    def __init__(self, addr = '0.0.0.0') :
        self.__rsa = crypto(secFile = 'server-private.pem', pubFile = 'server-public.pem')
        version = str(__version__)
        self.welcome = ','.join([version,crypto.sign_BASE64(version, self.__rsa.sec)]).encode('utf-8')
        self.entry = {
        'login': self.dealLogin,
        'switch': self.switcher,
        }
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind((addr,__port__))
        self.__socket.listen(5)
        print('Waiting for connection...')
        self.__user = {}
        self.run()

    def run(self) :
        while True :
            sock, addr = self.__socket.accept()
            t = threading.Thread(target=self.transfer, args=(sock, addr))
            #self.__list.append(t)
            t.start()

    def transfer(self, sock, addr) :
        print('Accept new connection from %s:%s...' % addr, color = 'g')
        #challenge = sock.recv(10240).decode('utf-8')
        #print('Accept challenge from %s:%s...' % addr, color = 'g')
        #crypto.sendSign(sock, challenge, self.__rsa.sec)
        data = crypto.recvDecrypted(sock, self.__rsa.sec)
        print(data)
        if data :
            self.router(Command.rebuild(data), sock)
        sock.close()
        print('Connection from %s:%s closed.' % addr, color = 'r')

    def router(self, command, sock) :
        #try :
        self.entry[command.type](command,sock)
        #except :
        #    crypto.sendWithSign(sock, 'Unknow Command', self.__rsa.sec)
        #    raise

    def dealLogin(self, info, sock) :
        if len(info.contents) != 3 :
            crypto.sendWithSign(sock, 'Invaild Syntax', self.__rsa.sec)
            return
        try :
            pub = RSA.importKey(info.contents[2].encode('utf-8'))
        except :
            crypto.sendWithSign(sock, 'Invaild Public Key', self.__rsa.sec)
            raise
            return
        try :
            user = self.__user[info.contents[0]]
            if user.isOnline :
                crypto.sendWithSign(sock, 'Already Online', self.__rsa.sec)
                return
            elif user.password != info.contents[1] :
                crypto.sendWithSign(sock, 'Access Denied', self.__rsa.sec)
                return
        except :
            user = User(info.contents[0], info.contents[1])
        crypto.sendWithSign(sock, 'Success', self.__rsa.sec)
        user.pubkey = pub
        user.isOnline = True
        user.token = crypto.random_str(32)
        crypto.sendEncrypted(sock, user.token, user.pubkey)
        self.__user[info.contents[0]] = user

    def switcher(self, info, sock) :
        if len(info.contents) != 3 :
            crypto.sendWithSign(sock, 'Invaild Syntax', self.__rsa.sec)
            return
        try :
            user = self.__user[info.contents[0]]
        except :
            crypto.sendWithSign(sock, 'User Not Found', self.__rsa.sec)
