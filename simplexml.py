__author__ = 'Administrator'
import xml.parsers.expat


class Node:
    def __init__(self, tag, attrs={}, namespace=None, parent=None, node_built=False):
        self.tag = tag
        self.attrs = attrs
        self.namespace = namespace
        self.kids = []
        self.name = ""
        self.parent = parent

        if tag:
            if node_built:
                self.namespace, self.name = ([""] + tag.split(":"))[-2:]
            else:
                if " " in tag:
                    self.namespace, self.name = tag.split()
                else:
                    self.name = tag

    def set_namespace(self, namespace):
        self.namespace = namespace

    def set_attrs(self, key, val):
        self.attrs[key] = val

    def __str__(self):
        s = "<"+self.name

        if self.namespace:
            if not self.parent or self.parent.namespace != self.namespace:
                if "xmlns" not in self.attrs:
                    s = s + (" xmlns='%s'" % self.namespace)

        for x in self.attrs.keys():
            s = s + (" %s='%s'" % (x, self.attrs[x]))
        s = s+">"

        if self.kids:
            pass

        if s.endswith(">"):
            s = s[:-1]+"/>"
        else:
            s = s + "<"+self.name+"/>"

        return s

    def get_tag(self, name):
        return None

    def get_name(self):
        return self.name


class NodeBuilt:
    def __init__(self):
        self.parse = xml.parsers.expat.ParserCreate()
        self.parse.StartElementHandler = self.start_tag
        self.parse.EndElementHandler = self.end_tag
        self.parse.CharacterDataHandler = self.handle_cdata
        self.parse.StartNamespaceDeclHandler = self.handle_namespace_start
        self.parse.buffer_text = True
        self.Parse = self.parse.Parse

        self._dispatch_depth = 1
        self.__depth = 0
        self.document_attrs = None
        self.document_nsp = None

        self.min_dom = None
        self._ptr = None

    def start_tag(self, tag, attrs):
        self.depth_inc()

        if self.__depth == 1:
            self.document_attrs = {}
            self.document_nsp = {}

            nsp, name = ([""] + tag.split(":"))[-2:]

            for attr, val in attrs.items():
                if attr == "xmlns":
                    self.document_nsp[u''] = val
                elif attr[:6] == "xmlns:":
                    self.document_nsp[attr[6:]] = val
                else:
                    self.document_attrs[attr] = val

            ns = self.document_nsp.get(nsp, 'http://www.gajim.org/xmlns/undeclared-root')
            try:
                self.stream_header_received(ns, name)
            except Exception as e:
                print e
                self.document_attrs = None
                raise ValueError(str(e))
        elif self.__depth == self._dispatch_depth:
            self.min_dom = Node(tag, attrs, self.document_nsp, node_built=True)
            self._ptr = self.min_dom
        elif self.__depth > self._dispatch_depth:
            self._ptr.kids.append(Node(tag, attrs, parent=self._ptr))
            self._ptr = self._ptr.kids[-1]

    def end_tag(self, tag):
        if self.__depth == self._dispatch_depth:
            self.dispatcher(self.min_dom)
        elif self.__depth > self._dispatch_depth:
            self._ptr = self._ptr.parent

        self.depth_dec()
        if self.__depth == 0:
            self.stream_footer_received()

    def handle_cdata(self, data):
        pass

    def handle_namespace_start(self):
        pass

    def depth_inc(self):
        self.__depth = self.__depth + 1

    def depth_dec(self):
        self.__depth = self.__depth - 1

    def stream_footer_received(self):
        pass