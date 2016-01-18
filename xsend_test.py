__author__ = 'Administrator'

from client import Client
from protocol import Message


server = "192.168.16.175"
port = 5222
user = "admin"
password = "123456"
resource = "py_client"
tojid = "sh@localhost/test"


def message_test():
    print Message(tojid, "today is a good day")


def send_xmpp():
    client_xmpp = Client(server, port)
    connect = client_xmpp.connect()
    print "connect is ", connect
    print client_xmpp.auth(user, password, resource)
    print "bind finish"
    client_xmpp.send(Message(tojid, "today is a good day"))

    client_xmpp.get_response()


if __name__ == "__main__":
    send_xmpp()