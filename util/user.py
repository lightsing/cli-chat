# -*- coding:utf-8 -*-
__author__ = 'lightsing'
import time
class User(object) :
    def __init__(self, username, password) :
        self.username = username
        self.password = password
        self.isOnline = False
        self.lastseen = time.time()
        self.token = ''
        self.contacts = []
        self.pubkey = None
