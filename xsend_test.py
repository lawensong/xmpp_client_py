__author__ = 'Administrator'

from client import Client


def send_xmpp(server, port, user, password, resource):
    client_xmpp = Client(server, port)
    connect = client_xmpp.connect()
    print "connect is ", connect
    client_xmpp.auth(user, password, resource)


if __name__ == "__main__":
    server = "192.168.1.220"
    port = 5222
    user = "admin"
    password = "123456"
    resource = "py_client"
    send_xmpp(server, port, user, password, resource)