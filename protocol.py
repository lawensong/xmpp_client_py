__author__ = 'Administrator'

from simplexml import Node


NS_SASL = 'urn:ietf:params:xml:ns:xmpp-sasl'                     # RFC 3920


class Jid:
    def __init__(self):
        pass


class Protocol(Node):
    def __init__(self):
        super(Protocol, self).__init__()


class Iq(Protocol):
    def __init__(self):
        super(Iq, self).__init__()


class Message(Protocol):
    def __init__(self):
        super(Message, self).__init__()


class Presence(Protocol):
    def __init__(self):
        super(Presence, self).__init__()