__author__ = 'Administrator'

from simplexml import Node


NS_SASL = 'urn:ietf:params:xml:ns:xmpp-sasl'                     # RFC 3920
NS_CLIENT = 'jabber:client'                                      # RFC 3921


class JID:
    def __init__(self, jid=None, node='', domain='', resource=''):
        if not jid and not node:
            raise ValueError("JID must contain at least domain name")
        elif type(jid) == type(self):
            self.node = jid.node
            self.domain = jid.domain
            self.resource = jid.resource
        elif domain:
            self.node = node
            self.domain = domain
            self.resource = resource
        else:
            if jid.find('@') + 1:
                self.node, jid = jid.split("@", 1)
            else:
                self.node = ''

            if jid.find('/') + 1:
                self.domain, self.resource = jid.split('/', 1)
            else:
                self.domain = jid
                self.resource = ''

    def get_node(self):
        return self.node

    def set_node(self, node):
        self.node = node.lower()

    def get_domain(self):
        return self.domain

    def set_domain(self, domain):
        self.domain = domain.lower()

    def get_resource(self):
        return self.resource

    def set_resource(self, resource):
        self.resource = resource


class Protocol(Node):
    def __init__(self, name=None, to=None, tye=None, frm=None, attrs={}, payload=[], xmlns=None, node=None):
        if not attrs:
            attrs = {}
        if to: attrs['to'] = to
        if tye: attrs['type'] = tye
        if frm: attrs['from'] = frm
        super(Protocol, self).__init__(tag=name, attrs=attrs, payload=payload, node=node)
        if self['to']:
            self.set_to(self['to'])
        if self['from']:
            self.set_from(self['from'])

    def get_to(self):
        return self.get_attrs('to')

    def set_to(self, val):
        return self.set_attrs('to', JID(val))

    def get_from(self):
        return self.get_attrs('from')

    def set_from(self, val):
        return self.set_attrs('from', JID(val))

    def get_id(self):
        return self.get_attrs('id')

    def set_id(self, val):
        return self.set_attrs('id', val)

    def get_type(self):
        return self.get_attrs('type')

    def set_type(self, val):
        return self.set_attrs('type', val)

    def get_properties(self):
        pops = []
        for node in self.get_children():
            pop = node.get_namespace()
            if pop not in pops:
                pops.append(pop)
        return pops


class Iq(Protocol):
    def __init__(self, query_ns=None, to=None, typ=None, frm=None, attrs={}, payload=[], xmlns=NS_CLIENT, node=None):
        super(Iq, self).__init__("iq", to=to, tye=typ, frm=frm, attrs=attrs, xmlns=xmlns, node=node)
        if query_ns:
            self.set_query_ns(query_ns)
        if payload:
            self.set_query_payload(payload)

    def get_query_ns(self):
        tag = self.get_tag('query')
        if tag:
            return tag.get_namespace()

    def set_query_ns(self, namespace):
        self.set_tag('query').set_namespace(namespace)

    def get_query_node(self):
        return self.get_tag_attr('query', 'node')

    def set_query_node(self, node):
        self.set_tag_attr('query', 'node', node)

    def get_query_payload(self):
        tag = self.get_tag('query')
        if tag:
            return tag.get_payload()

    def set_query_payload(self, payload):
        self.set_tag('query').set_payload(payload)

    def get_query_children(self):
        tag = self.get_tag('query')
        if tag:
            return tag.get_children()

    def build_reply(self, typ):
        iq = Iq(typ, to=self.get_from(), frm=self.get_to(), attrs={"id": self.get_id()})
        if self.get_tag("query"):
            iq.set_query_ns(self.get_query_ns())
        return iq


class Message(Protocol):
    def __init__(self, to=None, body=Node, subject=Node, frm=None, typ=None, attrs={}, payload=[], xmlns=NS_CLIENT, node=None):
        super(Message, self).__init__("message", to=to, tye=typ, frm=frm, attrs=attrs, payload=payload, xmlns=xmlns, node=node)
        if body:
            self.set_body(body)
        if subject:
            self.set_subject(subject)

    def get_body(self):
        return self.get_tag_data('body')

    def set_body(self, body):
        self.set_tag_data('body', body)

    def get_subject(self):
        return self.get_tag_data('subject')

    def set_subject(self, val):
        self.set_tag_data('subject', val)

    def get_thread(self):
        return self.get_tag_data('thread')

    def set_thraed(self, val):
        self.set_tag_data('thread', val)

    def build_reply(self, text=None):
        message = Message(to=self.get_from(), frm=self.get_to(), body=text)
        if self.get_thread():
            message.set_thraed(self.get_thread())
        return message


class Presence(Protocol):
    def __init__(self, to=None, priority=None, status=None, show=None, frm=None, typ=None, attrs={}, payload=[], xmlns=NS_CLIENT, node=None):
        super(Presence, self).__init__('presence', to=to, tye=typ, frm=frm, attrs=attrs, payload=payload, xmlns=xmlns, node=node)
        if priority:
            self.set_priority(priority)
        if status:
            self.set_status(status)
        if show:
            self.set_show(show)

    def get_priority(self):
        return self.get_tag_data('priority')

    def set_priority(self, priority):
        self.set_tag_data("priority", priority)

    def get_show(self):
        return self.get_tag_data('show')

    def set_show(self, show):
        self.set_tag_data('show', show)

    def get_status(self):
        return self.get_tag_data('status')

    def set_status(self, status):
        self.set_tag_data('status', status)