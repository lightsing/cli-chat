# -*- coding:utf-8 -*-
__author__ = 'lightsing'

import util

ssl_sock = util.creatSSLSocks(isServer = True)
conn, addr = ssl_sock.accept()
print(conn.recv(1024))
conn.send(b'Server Hello')
