# -*- coding:utf-8 -*-
__author__ = 'lightsing'

import time, base64
from Crypto import Random
from random import Random as sysRandom
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Cipher import PKCS1_v1_5 as Cipher
from Crypto.Signature import PKCS1_v1_5 as Signature
random_generator = Random.new().read

class Operator(object) :
    def __init__(self, secFile = '', pubFile = '', remote = '', opt_len = 4096) :
        if secFile and pubFile :
            with open(secFile) as f:
                sec = f.read()
            with open(pubFile) as f:
                pub = f.read()
        else :
            rsa = Operator.generateRSA(len = opt_len)
            sec = rsa.exportKey()
            pub = rsa.publickey().exportKey()
        self.sec = RSA.importKey(sec)
        self.pub = RSA.importKey(pub)
        if remote :
            with open(remote) as f:
                remote = f.read()
            self.remote = RSA.importKey(remote)

    def encrypt(message, key) :
        cipher = Cipher.new(key)
        data = cipher.encrypt(message)
        return data
    def encrypt_BASE64(message, key) :
        return base64.b64encode(Operator.encrypt(message.encode('utf-8'), key)).decode('utf-8')

    def decrypt(data, key) :
        cipher = Cipher.new(key)
        return cipher.decrypt(data, random_generator)
    def decrypt_BASE64(data, key) :
        cipher = Cipher.new(key)
        return cipher.decrypt(base64.b64decode(data), random_generator).decode('utf-8')

    def sign(message, key) :
        return Signature.new(key).sign(SHA256.new(message.encode('utf-8')))
    def sign_BASE64(message, key) :
        return base64.b64encode(Operator.sign(message, key)).decode('utf-8')
    def verify(message, signature, key) :
        return Signature.new(key).verify(SHA256.new(message.encode('utf-8')), base64.b64decode(signature))

    def random_str(randomlength=8):
        str = ''
        chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
        length = len(chars) - 1
        random = sysRandom()
        for i in range(randomlength):
            str+=chars[random.randint(0, length)]
        return str

    def generateRSA(len = 4096) :
        random = Random.new().read
        print('\nGengerating RSA Key Pair......\n')
        rsa = RSA.generate(len, random)
        return rsa

    def writeoutRSA(rsa, name, switch = True) :
        private_pem = rsa.exportKey()
        if switch:
            with open('%s-private.pem' % name, 'wb') as f :
                f.write(private_pem)
        public_pem = rsa.publickey().exportKey()
        with open('%s-public.pem' % name, 'wb') as f :
            f.write(public_pem)

    def validateServer(sock, pub) :
        challenge = Operator.random_str()
        sock.send(challenge.encode('utf-8'))
        signature = sock.recv(1024).decode('utf-8')
        if not Operator.verify(challenge, signature, pub) :
            print('CANNOT Trust Server, MITM Attack Warning.')
            exit(-1)

    def sendWithSign(sock, data, sec) :
        signature = Operator.sign_BASE64(data, sec)
        message = ':'.join([data, signature])
        try :
            sock.send(message.encode('utf-8'))
        except :
            print('Connection Error')
            sock.close()
            return
    def sendSign(sock, data, sec) :
        signature = Operator.sign_BASE64(data, sec)
        try :
            sock.send(signature.encode('utf-8'))
        except :
            print('Connection Error')
            sock.close()
            return
    def recvWithSign(sock, pub) :
        data = sock.recv(10240)
        if not data :
            sock.close()
            return
        content = data.decode('utf-8').split(':')
        length = len(content)
        if length != 2 :
            raise Exception("Invalid Content Length!", length)
        if Operator.verify(content[0], content[1], pub) :
            return content[0]
        else :
            raise Exception("Verify Signature Error.", content)

    def sendEncrypted(sock, data, pub) :
        data = Operator.addTimestamp(data)
        try :
            sock.send(Operator.encrypt(data.encode('utf-8'), pub))
        except :
            print('Connection Error')
            sock.close()
            return
    def recvDecrypted(sock, sec) :
        data = sock.recv(10240)
        if not data :
            sock.close()
            return
        message = Operator.decrypt(data, sec)
        return message.decode('utf-8')
    def addTimestamp(data) :
        return data
    def filterReplayAttack(data) :
        return data
        '''
        now = time.time()
        length = len(data)
        if length < 2 :
            print('Invalid Content Length!')
            return
        try :
            sendTime = float(data.pop())
            delay = now - sendTime
        except :
            print('Invalid Timestamp')
            return
        if delay < 30 and delay > 0 :
            return data
        else :
            return
        '''
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
