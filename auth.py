__author__ = 'Administrator'
import base64

from utils import Plugin
from protocol import NS_SASL
from simplexml import Node


class SASL(Plugin):
    def __init__(self, username, password):
        super(Plugin, self).__init__()
        self.username = username
        self.password = password

        self.export_method = []

    def plugin(self):
        try:
            self.features_handler(self.owner.Dispatcher, self.owner.Dispatcher.stream.features)
        except Exception as e:
            print e

    def features_handler(self, dis, feature):
        if not feature.get_tag("mechanisms", namespace=NS_SASL):
            self.startsasl = "not-supported"
            return

        mecs = []
        for mec in feature.get_tag("mechanisms", namespace=NS_SASL).get("mechanism"):
            mecs.append(mec.get_data())

        self.owner.register_handler("challenge", self.sasl_handler, xmlns=NS_SASL)
        self.owner.register_handler("failure", self.sasl_handler, xmlns=NS_SASL)
        self.owner.register_handler("success", self.sasl_handler, xmlns=NS_SASL)

        if "ANONYMOUS" in mecs and self.username == None:
            node = Node('auth', attrs={"xmlns": NS_SASL, "mechanism": "ANONYMOUS"})
        elif "DIGEST-MD5" in mecs:
            node = Node('auth', attrs={"xmlns": NS_SASL, "mechanism": "DIGEST-MD5"})
        elif "PLAIN" in mecs:
            sasl_data= "%s\x00%s\x00%s" % (self.username+'@'+self.owner.server, self.username, self.password)
            node = Node('auth', attrs={"xmlns": NS_SASL, "mechanism": "PLAIN"}, payload=[base64.encodestring(sasl_data).replace('\r', '').replace('\n','')])
        else:
            self.startsasl = "fail"
            return

        self.startsasl = "in-process"
        self.owner.send(str(node))

    def sasl_handler(self, conn, challenge):
        pass