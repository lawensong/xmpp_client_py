__author__ = 'Administrator'

import transports


class Client:
    def __init__(self, server, port):
        self.server = server
        self.port = port
        self.namespace = "jabber:client"

    def connect(self):
        pass
