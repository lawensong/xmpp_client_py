__author__ = 'Administrator'

from transports import TcpSocket
from dispatcher import Dispatcher


class Client:
    def __init__(self, server, port):
        self.server = server
        self.port = port
        self.namespace = "jabber:client"

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

    def auth(self):
        pass