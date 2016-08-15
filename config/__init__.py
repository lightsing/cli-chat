# -*- coding:utf-8 -*-
__author__ = 'lightsing'

import ssl

__version__ = 0.1

PORT = 9999
ADDR = ('127.0.0.1', port)

SSL_VERSION = ssl.PROTOCOL_TLSv1.2
SSL_CIPHERS = None

SSL_CERT_REQS = ssl.CERT_REQUIRED
# SSL_CERT_REQS = ssl.CERT_OPTIONAL
SSL_KEY_FILE = 'key.pem'
SSL_CERT_FILE = 'server.crt'
SSL_CA_CERT = 'ca.crt'
