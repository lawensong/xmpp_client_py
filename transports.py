__author__ = 'Administrator'
import socket
import select

from utils import Plugin
import xlog

log = xlog.get_log()
BUFLEN = 1024


class TcpSocket(Plugin):
    def __init__(self, server, port):
        super(TcpSocket, self).__init__()
        self.server = server
        self.port = port
        self.sock = None
        self._send = None
        self._recv = None

        self.export_method = [self.send, self.receive]

    def get_host(self):
        return self.server

    def get_port(self):
        return self.port

    def plugin(self, owner):
        self.connect()
        self.owner.connection = self

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server, int(self.port)))
            self._send = self.sock.sendall
            self._recv = self.sock.recv
            log.debug("success connect to server: %s port: %s" % (self.server, self.port))
        except Exception as e:
            log.debug("fail connect to server, msg: %s" % e)

    def disconnect(self):
        log.debug("disconnect to server")
        self.sock.close()

    def receive(self):
        try:
            received = self._recv(BUFLEN)
        except Exception as e:
            print e
            received = ""

        while self.pending_data(0):
            try:
                add = self._recv(BUFLEN)
            except Exception as e:
                print e
                add = ""

            received += add
            if not add:
                break
        return received

    def pending_data(self, timeout=0):
        return select.select([self.sock], [], [], timeout)[0]

    def send(self, raw_data):
        try:
            self._send(raw_data)
        except Exception as e:
            print e