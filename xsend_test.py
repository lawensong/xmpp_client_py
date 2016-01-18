__author__ = 'Administrator'
import threading

from client import Client
from protocol import Message


CLIENT = None
server = "192.168.16.175"
port = 5222
user = "shnanyang"
password = "123456"
resource = "py_client1"
tojid = "admin@localhost/test"


def message_test():
    print Message(tojid, "today is a good day")


def send_xmpp():
    client_xmpp = Client(server, port)
    connect = client_xmpp.connect()
    print "connect is ", connect
    print client_xmpp.auth(user, password, resource)
    client_xmpp.register_h()
    client_xmpp.register_message()
    # client_xmpp.send(Message(tojid, "today is a good day"))
    print "start to get response"
    global CLIENT
    CLIENT = client_xmpp
    threading.Thread(target=xshell).start()
    client_xmpp.get_response(client_xmpp.send, Message(tojid, "today is a good day"))


def xshell():
    while True:
        xstr = raw_input('>>')
        try:
            print "input: ", xstr
            if not xstr:
                continue
            elif xstr.strip() == "exit":
                exit()
            else:
                CLIENT.send(Message(tojid, xstr))
        except Exception as e:
            print e


if __name__ == "__main__":
    send_xmpp()