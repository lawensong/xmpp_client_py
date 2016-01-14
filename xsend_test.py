__author__ = 'Administrator'

from client import Client


def send_xmpp(server, port):
    client_xmpp = Client(server, port)
    client_xmpp.connect()


if __name__ == "__main__":
    server = "192.168.16.175"
    port = 5222
    send_xmpp(server, port)