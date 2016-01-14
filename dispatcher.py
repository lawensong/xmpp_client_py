__author__ = 'Administrator'


import simplexml
from utils import Plugin
from protocol import Protocol, Iq, Presence, Message


class Dispatcher(Plugin):
    def __init__(self):
        super(Dispatcher, self).__init__()
        self.handlers = {}

        self.export_method = [self.process]

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
        self.stream.stream_header_received = self.stream_header_received

        self._metastream = simplexml.Node("stream:stream")
        self._metastream.set_namespace(self.owner.namespace)
        self._metastream.set_attrs("to", "localhost")
        self._metastream.set_attrs("version", "1.0")
        self._metastream.set_attrs("xmlns:stream", "http://etherx.jabber.org/streams")
        print "--->>><?xml version='1.0'?>%s>" % str(self._metastream)[:-2]
        self.owner.send("<?xml version='1.0'?>%s>" % str(self._metastream)[:-2])

    def plugin(self, owner):
        self._init()
        self.stream_init()

    def register_namespace(self, xmlns):
        self.handlers[xmlns] = {}
        self.register_protocol("unknown", Protocol, xmlns)
        self.register_protocol("default", Protocol, xmlns)

    def register_protocol(self, tag_name, protocol, xmlns):
        self.handlers[xmlns][tag_name] = {"type": protocol, "default": []}

    def process(self, timeout=0):
        if self.owner.connection.pending_data(timeout):
            data = self.owner.connection.receive()
            if data:
                print "---<<<", data
                self.stream.Parse(data)
                return len(data)
        return None

    def dispatcher(self, stanza):
        if stanza.get_name() == "features":
            self.stream.features = stanza

        print "dispatcher", stanza

    def stream_header_received(self, nsp, name):
        if nsp != 'http://etherx.jabber.org/streams' or name != "stream":
            raise ValueError('Incorrect stream start: (%s,%s). Terminating.'%(name, nsp))