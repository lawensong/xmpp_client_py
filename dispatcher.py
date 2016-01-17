__author__ = 'Administrator'


import simplexml
from utils import Plugin
from protocol import Protocol, Iq, Presence, Message


class Dispatcher(Plugin):
    def __init__(self):
        super(Dispatcher, self).__init__()
        self.handlers = {}

        self.export_method = [self.process, self.register_handler]

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

    def register_handler(self, name, handler, type='', ns='', xmlns='', first=0, system=0):
        if not xmlns:
            xmlns = self.owner.namespace

        if not type and not ns:
            type = "default"

        if not self.handlers.has_key(xmlns):
            self.register_namespace(xmlns)

        if not self.handlers[xmlns].has_key(name):
            self.register_protocol(name, Protocol, xmlns)

        if not self.handlers[xmlns][name].has_key(type+ns):
            self.handlers[xmlns][name][type+ns] = []

        if first:
            self.handlers[xmlns][name][type+ns].insert(0, {"func": handler, "system": system})
        else:
            self.handlers[xmlns][name][type+ns].append({"func": handler, "system": system})

    def process(self, timeout=0):
        if self.owner.connection.pending_data(timeout):
            try:
                data = self.owner.connection.receive()
            except Exception as e:
                print e
                return
            if data:
                print "---<<<", data
                self.stream.Parse(data)
                return len(data)
        return '0'

    def dispatcher(self, stanza, session=None):
        if not session:
            session = self
        session.stream.min_dom = None
        name = stanza.get_name()
        if name == "features":
            self.stream.features = stanza

        xmlns = stanza.get_namespace()

        if not self.handlers.has_key(xmlns):
            xmlns = "unknown"
        if not self.handlers[xmlns].has_key(name):
            name = "unknown"

        if stanza.__class__.__name__ == "Node":
            stanza = self.handlers[xmlns][name]["type"](node=stanza)

        typ = stanza.get_type()
        if not typ:
            typ = ""
        stanza.pops = stanza.get_properties()

        hlist = ["default"]
        if self.handlers[xmlns][name].has_key(typ):
            hlist.append(typ)
        for p in stanza.pops:
            if self.handlers[xmlns][name].has_key(p):
                hlist.append(p)
            if self.handlers[xmlns][name].has_key(typ+p):
                hlist.append(typ+p)

        chain = self.handlers[xmlns]['default']['default']
        for key in hlist:
            if key:
                chain = chain + self.handlers[xmlns][name][key]

        user = 1
        for handler in chain:
            if user or handler['system']:
                try:
                    handler['func'](session, stanza)
                except Exception as e:
                    print e
                    user = 0

    def stream_header_received(self, nsp, name):
        if nsp != 'http://etherx.jabber.org/streams' or name != "stream":
            raise ValueError('Incorrect stream start: (%s,%s). Terminating.'%(name, nsp))