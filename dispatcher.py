__author__ = 'Administrator'


import simplexml
from utils import Plugin
from protocol import Protocol, Iq, Presence, Message


class Dispatcher(Plugin):
    def __init__(self):
        super(Dispatcher, self).__init__()
        self.handlers = []

        self.export_method = []

    def _init(self):
        self.register_namespace("unknown")
        self.register_namespace("http://etherx.jabber.org/streams")
        self.register_namespace("jabber:client")

        self.register_protocol("iq", Iq, "jabber:client")
        self.register_protocol("message", Message, "jabber:client")
        self.register_protocol("presence", Presence, "jabber:client")

    def stream_init(self):
        self.stream = simplexml.NodeBuilt()
        self.stream._dispatch_depth = 2
        self.stream.dispatcher = self.dispatcher
        self.stream.features = None

        self._metastream = simplexml.Node("stream:stream")
        self._metastream.set_namespace(self.owner.namespace)
        self._metastream.set_attrs("to", self.owner.server)
        self._metastream.set_attrs("version", "1.0")
        self._metastream.set_attrs("xmlns:stream", "http://etherx.jabber.org/streams")
        self.owner.send()

    def plugin(self):
        self._init()
        self.stream_init()

    def register_namespace(self, xmlns):
        self.handlers[xmlns] = {}
        self.register_protocol("unknown", Protocol, xmlns)
        self.register_protocol("default", Protocol, xmlns)

    def register_protocol(self, tag_name, protocol, xmlns):
        self.handlers[xmlns][tag_name] = {"type": protocol, "default": []}

    def process(self, timeout=0):
        pass

    def dispatcher(self, stanza):
        pass