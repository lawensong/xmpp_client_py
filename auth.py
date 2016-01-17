__author__ = 'Administrator'
import base64
import re
import random
import md5
def HH(some): return md5.new(some).hexdigest()
def H(some): return md5.new(some).digest()
def C(some): return ':'.join(some)

from utils import Plugin
from protocol import NS_SASL
from simplexml import Node


class SASL(Plugin):
    def __init__(self, username, password):
        super(Plugin, self).__init__()
        self.username = username
        self.password = password

        self.export_method = []

    def plugin(self, owner):
        try:
            self.features_handler(self.owner.Dispatcher, self.owner.Dispatcher.stream.features)
        except Exception as e:
            print e

    def features_handler(self, dis, feature):
        if not feature.get_tag("mechanisms", namespace=NS_SASL):
            self.startsasl = "not-supported"
            return

        mecs = []
        for mec in feature.get_tag("mechanisms", namespace=NS_SASL).get_tags("mechanism"):
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
        if challenge.get_namespace() != NS_SASL:
            return

        if challenge.get_name() == "failure":
            self.startsasl = "failure"
            try:
                reason = challenge.get_children()[0]
            except Exception as e:
                print e
                reason = challenge
            print str(reason)
            return
        elif challenge.get_name() == "success":
            self.startsasl = "success"
            return
        else:
            incoming_data = challenge.get_data()
            data=base64.decodestring(incoming_data)
            chal = {}
            for pair in re.findall('(\w+\s*=\s*(?:(?:"[^"]+")|(?:[^,]+)))', data):
                key, val = [x.strip() for x in pair.split("=", 1)]
                if val[0] == '"' and val[-1] == '"':
                    val = val[1:-1]
                chal[key] = val

            if chal.has_key("qop") and "auth" in [x.strip() for x in chal['qop'].split(",")]:
                res = {}
                res['username'] = self.username
                res['realm'] = self.owner.server
                res['nonce'] = chal['nonce']
                cnonce = ''
                for i in range(7):
                    cnonce += hex(int(random.random()*65536*4096))[2:]
                res['cnonce'] = cnonce
                res['nc'] = ('00000001')
                res['qop'] = 'auth'
                res['digest-uri'] = 'xmpp/localhost'
                A1 = C([H(C([res['username'], res['realm'], self.password])), res['nonce'], res['cnonce']])
                A2 = C(['AUTHENTICATE', res['digest-uri']])
                response = HH(C([HH(A1), res['nonce'], res['nc'], res['cnonce'], res['qop'], HH(A2)]))
                res['response'] = response
                res['charset'] = 'utf-8'
                sasl_data = ''
                for key in ['charset', 'username', 'realm', 'nonce', 'nc', 'cnonce', 'digest-uri', 'response', 'qop']:
                    if key in ['nc', 'qop', 'response', 'charset']:
                        sasl_data += "%s=%s," % (key, res[key])
                    else:
                        sasl_data += '%s="%s",' % (key, res[key])
                node = Node("response", attrs={'xmlns': NS_SASL}, payload=[base64.encodestring(sasl_data[:-1]).replace('\r', '').replace('\n', '')])
                self.owner.send(str(node))
            elif chal.has_key("rspauth"):
                node = Node("response", attrs={'xmlns': NS_SASL})
                self.owner.send(str(node))
            else:
                self.startsasl = "failure"
