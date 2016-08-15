# -*- coding:utf-8 -*-
__author__ = 'lightsing'

import time, base64
from Crypto import Random
from random import Random as sysRandom
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Cipher import PKCS1_v1_5 as Cipher
from Crypto.Signature import PKCS1_v1_5 as Signature
random_generator = Random.new().read

from util import myprint as print

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

    def encryptAES(text, key):
        try:
            iv = Random.new().read(AES.block_size)
            cryptor = AES.new(key, AES.MODE_CBC, iv)
            length = 16
            count = len(text)
            add = length - (count % length)
            text = text + ('\0' * add)
            ciphertext = cryptor.encrypt(text)
        except :
            print('AES Encrypt ERROR',color='r')
            return
        return base64.b64encode(iv + ciphertext)

    def decryptAES(data, key):
        try:
            raw = data
            iv = raw[:AES.block_size]
            cryptor = AES.new(key, AES.MODE_CBC, iv)
            plain_text = cryptor.decrypt(raw[AES.block_size:]).decode().rstrip('\0')
        except :
            print('AES Decrypt ERROR',color='r')
            raise
            return
        return plain_text
    def sendEncryptedAES(sock, data, key) :
        data = Operator.addTimestamp(data)
        try :
            sock.send(Operator.encryptAES(data, key))
        except :
            print('Connection Error')
            sock.close()
            return
    def recvDecryptedAES(sock, key) :
        data = sock.recv(10240)
        if not data :
            sock.close()
            return
        message = Operator.decryptAES(data, key)
        return message

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
