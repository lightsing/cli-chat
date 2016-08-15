# -*- coding:utf-8 -*-
import socket, threading, time, threading, base64
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
        'logout': self.dealLogout,
        'online': self.keepOnline,
        'switch': self.switcher,
        }
        self.switch = {
        'find': self.switchFind,
        'send': self.switchSend,
        'sendDirect': self.switchSendDirect,
        'getUnread': self.switchGetUnread,
        }
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.bind((addr,__port__))
        self.__socket.listen(5)
        print('Waiting for connection...')
        self.__user = {}
        self.userMutex = threading.Lock()
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
        user = self.getUser(info.contents[0])
        if user :
            if user.isOnline :
                crypto.sendWithSign(sock, 'Already Online', self.__rsa.sec)
                return
            elif user.password != info.contents[1] :
                crypto.sendWithSign(sock, 'Access Denied', self.__rsa.sec)
                return
        else :
            user = User(info.contents[0], info.contents[1])
        crypto.sendWithSign(sock, 'Success', self.__rsa.sec)
        user.pubkey = pub
        user.isOnline = True
        user.token = crypto.random_str(16)
        crypto.sendEncrypted(sock, user.token, user.pubkey)
        self.editUser(info.contents[0], user)

    def dealLogout(self, info, sock):
        if len(info.contents) != 2 :
            crypto.sendWithSign(sock, 'Invaild Syntax', self.__rsa.sec)
            return
        user = self.getUser(info.contents[0])
        if not user :
            crypto.sendWithSign(sock, 'User Not Found', self.__rsa.sec)
            return
        if user.token == info.contents[1] :
            user.isOnline = False
            user.lastseen = time.time()
            user.token = ''
            self.editUser(info.contents[0], user)
            crypto.sendWithSign(sock, 'Success', self.__rsa.sec)
        else :
            crypto.sendWithSign(sock, 'User Not Found', self.__rsa.sec)
        return


    def keepOnline(self, info, sock):
        if len(info.contents) != 2 :
            crypto.sendWithSign(sock, 'Invaild Syntax', self.__rsa.sec)
            return
        user = self.getUser(info.contents[0])
        if not user :
            crypto.sendWithSign(sock, 'User Not Found', self.__rsa.sec)
            return
        if user.token == info.contents[1] :
            user.lastseen = time.time()
            self.editUser(info.contents[0], user)
            crypto.sendWithSign(sock, 'Success', self.__rsa.sec)
        else :
            crypto.sendWithSign(sock, 'User Not Found', self.__rsa.sec)
        return

    def switcher(self, info, sock) :
        if len(info.contents) != 4 :
            crypto.sendWithSign(sock, 'Invaild Syntax', self.__rsa.sec)
            return
        user = self.getUser(info.contents[0])
        if not user :
            crypto.sendWithSign(sock, 'User Not Found', self.__rsa.sec)
        if user.token == info.contents[1] :
            crypto.sendWithSign(sock, 'Accepted', self.__rsa.sec)
            self.switch[info.contents[2]](user, info.contents[3], sock)
        else :
            crypto.sendWithSign(sock, 'User Not Found', self.__rsa.sec)
        return

    def switchFind(self, user, data, sock) :
        username = crypto.decryptAES(base64.b64decode(data.encode()),user.token)
        target = self.getUser(username)
        if target :
            response = ','.join([str(target.isOnline),\
                     str(target.lastseen),\
                     target.pubkey.exportKey().decode('utf-8')])
            print('Ready to response:\n%s\n' % response ,color='b')
        else :
            response = 'User Not Found'
        #crypto.sendEncryptedAES(sock, response, user.token)
        response = crypto.encryptAES(response, user.token)
        print('Will send encrypted data:\n%s\n' % response ,color='r')
        sock.send(response)
        return
    def switchSend(self, user, data, sock) :
        return
    def switchSendDirect(self, user, data, sock) :
        return
    def switchGetUnread(self, user, data, sock) :
        return

    '''
    Threading Safe User Operation
    '''
    def editUser(self, key, user) :
        if self.userMutex.acquire():
            try :
                self.__user[key] = user
            except :
                raise
            self.userMutex.release()
    def getUser(self, key) :
        user = None
        if self.userMutex.acquire():
            try :
                user = self.__user[key]
            except :
                print('User %s not found' % key,color = 'r')
            self.userMutex.release()
        return user
