# -*- coding:utf-8 -*-
__author__ = 'lightsing'

import ssl

__version__ = 0.1

PORT = 8000
ADDR = ('127.0.0.1', PORT)

SSL_VERSION = ssl.PROTOCOL_TLSv1
SSL_CIPHERS = None

SSL_CERT_REQS = ssl.CERT_OPTIONAL
SSL_KEY_FILE = 'server.pem'
SSL_CERT_FILE = 'server.crt'
