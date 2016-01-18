__author__ = 'Administrator'
import time

from transports import TcpSocket
from dispatcher import Dispatcher
from auth import SASL, Bind
from protocol import NS_SESSION_TWO
from simplexml import Node


R_H = 1


class Client:
    def __init__(self, server, port):
        self.server = server
        self.port = port
        self.namespace = "jabber:client"

        self.user = ""
        self.password = ""
        self.resource = ""

    def connect(self):
        TcpSocket(self.server, self.port).Plugin(self)
        self.connected = "tcp"

        Dispatcher().Plugin(self)

        while self.Dispatcher.stream.document_attrs is None:
            if not self.process(1):
                return

        if self.Dispatcher.stream.document_attrs.get("version") == "1.0":
            while not self.Dispatcher.stream.features and self.process(1):
                pass

        if not self.Dispatcher.stream.features.get_tag("starttls"):
            return self.connected

    def auth(self, user, password, resource=""):
        self.user = user
        self.password = password
        self.resource = resource
        SASL(user, password).Plugin(self)

        if self.SASL.startsasl == "not-supported":
            return

        while self.SASL.startsasl == "in-process" and self.process(1):
            pass

        if self.SASL.startsasl == "success":
            Bind().Plugin(self)
            while self.Bind.bound is None and self.process(1):
                pass

            if self.Bind.bind(self.resource):
                self.connected += 'sasl'
                return 'sasl'
        else:
            print 'SASL error'

    def register_h(self):
        self.register_handler('r', self.handler_a, xmlns=NS_SESSION_TWO)

    def handler_a(self, dis, stanza):
        global R_H
        R_H += 1
        _id = R_H
        self.send(Node('a', attrs={'xmlns': NS_SESSION_TWO, 'h': _id}))

    def register_message(self):
        self.register_handler('message', self.handler_message)

    def handler_message(self, dis, stanza):
        print str(stanza.get_from())+": "+stanza.get_tag_data('body')

    def get_response(self, func=None, text=""):
        while True:
            self.process(1)
            # if func:
            #     func(text)