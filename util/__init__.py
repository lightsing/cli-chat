# -*- coding:utf-8 -*-
__author__ = 'lightsing'
import config

import socket, ssl

def creatSSLSocks(isServer = False) :
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if isServer :
        ssl_sock = ssl.wrap_socket(conn,
                                   server_side = True,
                                   certfile = config.SSL_CERT_FILE,
                                   keyfile = config.SSL_KEY_FILE,
                                   ssl_version = config.SSL_VERSION,
                                   cert_reqs = config.SSL_CERT_REQS)
        ssl_sock.bind(config.ADDR)
        ssl_sock.listen(5)
    else :
        ssl_sock = ssl.wrap_socket(conn,
                                   ca_certs = config.SSL_CERT_FILE,
                                   ssl_version = config.SSL_VERSION,
                                   cert_reqs = config.SSL_CERT_REQS)
        ssl_sock.connect(config.ADDR)
    return ssl_sock
