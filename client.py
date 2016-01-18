__author__ = 'Administrator'

from transports import TcpSocket
from dispatcher import Dispatcher
from auth import SASL, Bind


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

    def get_response(self):
        print "start to get response"
        while self.process(1):
            pass