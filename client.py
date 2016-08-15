# -*- coding:utf-8 -*-
__author__ = 'lightsing'

import util

ssl_sock = util.creatSSLSocks()
ssl_sock.send(b'Client Hello')
print(ssl_sock.recv(1024))
