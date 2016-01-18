__author__ = 'Administrator'
import xml.parsers.expat


class Node(object):
    def __init__(self, tag, attrs={}, namespace=None, parent=None, node_built=False, payload=[], node=None):
        self.tag = tag
        self.attrs = {}
        self.namespace = namespace
        self.namespace_cache = {}
        self.nsd = {}
        self.kids = []
        self.name = ""
        self.parent = parent
        self.data = []

        if node:
            self.name = node.name
            self.namespace = node.namespace
            self.parent = node.parent
            for key in node.attrs.keys():
                self.attrs[key] = node.attrs[key]
            for data in node.data:
                self.data.append(data)
            for kid in node.kids:
                self.kids.append(kid)
            for key in node.nsd.keys():
                self.nsd[key] = node.nsd[key]

        for attr, val in attrs.items():
            if attr == "xmlns":
                self.nsd[u''] = val
            elif attr.startswith("xmlns:"):
                self.nsd[attr[6:]] = val
            self.attrs[attr] = val

        if namespace:
            for key in namespace.keys():
                self.namespace_cache[key] = namespace[key]

        if tag:
            if node_built:
                pfx, self.name = ([""] + tag.split(":"))[-2:]
                self.namespace = self.lookup_nsp(pfx)
            else:
                if " " in tag:
                    self.namespace, self.name = tag.split()
                else:
                    self.name = tag

        if isinstance(payload, basestring):
            payload = [payload]

        for x in payload:
            if isinstance(x, Node):
                self.add_children(node = x)
            else:
                self.data.append(x)

    def lookup_nsp(self, pfx=''):
        ns = self.nsd.get(pfx, None)
        if not ns:
            ns = self.namespace_cache.get(pfx, None)
        if not ns:
            if self.parent:
                ns = self.parent.lookup_nsp(pfx)
                self.namespace_cache[pfx] = ns
            else:
                return 'http://www.gajim.org/xmlns/undeclared'
        return ns

    def set_namespace(self, namespace):
        self.namespace = namespace

    def get_namespace(self):
        return self.namespace

    def set_parent(self, parent):
        self.parent = parent

    def get_parent(self):
        return self.parent

    def set_attrs(self, key, val):
        self.attrs[key] = val

    def get_attrs(self, key):
        return self.attrs.get(key)

    def __str__(self):
        s = "<"+self.name

        if self.namespace:
            if not self.parent or self.parent.namespace != self.namespace:
                if "xmlns" not in self.attrs:
                    s = s + (" xmlns='%s'" % self.namespace)

        for x in self.attrs.keys():
            s = s + (" %s='%s'" % (x, str(self.attrs[x])))
        s = s+">"

        if self.kids:
            for a in self.kids:
                s = s + str(a)

        if self.data:
            for dd in self.data:
                s = s + dd

        if not self.kids and s.endswith(">"):
            s = s[:-1]+"/>"
        else:
            s = s + "</"+self.name+">"

        return s

    def add_children(self, name=None, attrs={}, namespace=None, payload=[], node=None):
        if node:
            new_node = node
            node.parent = self
        else:
            new_node = Node(name, attrs=attrs, payload=payload, parent=self)

        if namespace:
            new_node.set_namespace(namespace)

        self.kids.append(new_node)
        return new_node

    def get_tag(self, name, attrs={}, namespace=None):
        return self.get_tags(name, attrs, namespace, one=1)

    def set_tag(self, name, attrs={}, namespace=None):
        node = self.get_tag(name, attrs, namespace)
        if node:
            return node
        else:
            return self.add_children(name, attrs=attrs, namespace=namespace)

    def get_tags(self, name, attrs={}, namespace=None, one=0):
        nodes = []
        for node in self.kids:
            if not node:
                continue
            if namespace and namespace != node.get_namespace():
                continue
            if name == node.get_name():
                for key in attrs.keys():
                    if key not in node.attrs or node.attrs[key] != attrs[key]:
                        break
                nodes.append(node)
                if one == 1:
                    return nodes[0]
        if not one:
            return nodes

    def get_name(self):
        return self.name

    def get_data(self):
        return "".join(self.data)

    def get_children(self):
        return self.kids

    def get_tag_data(self, tag):
        try:
            return self.get_tag(tag).get_data()
        except Exception as e:
            return None

    def set_tag_data(self, tag, val, attrs={}):
        try:
            self.get_tag(tag, attrs=attrs).set_data(val)
        except Exception as e:
            self.add_children(tag, attrs, payload=[val])

    def get_tag_attr(self, tag, attr):
        return self.get_tag(tag).attrs[attr]

    def set_tag_attr(self, tag, attr, val):
        try:
            self.get_tag(tag).attrs[attr] = val
        except Exception as e:
            print e
            self.add_children(tag, attrs={attr: val})

    def get_payload(self):
        ret = []
        for i in range(max(len(self.data), len(self.kids))):
            if i< len(self.data):
                ret.append(self.data)
            if i< len(self.kids):
                ret.append(self.kids)
        return ret

    def set_payload(self, payload, add=0):
        if add:
            self.kids = payload
        else:
            self.kids += payload

    def __getitem__(self, item):
        return self.get_attrs(item)

    def __setitem__(self, key, val):
        return self.set_attrs(key, val)


class NodeBuilt(object):
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
        self.data_buffer = None

    def check_data_buffer(self):
        if self.data_buffer:
            self._ptr.data.append(''.join(self.data_buffer))
            del self.data_buffer[:]
            self.data_buffer = None

    def start_tag(self, tag, attrs):
        self.check_data_buffer()
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
            self._ptr.kids.append(Node(tag, attrs, parent=self._ptr, node_built=True))
            self._ptr = self._ptr.kids[-1]

    def end_tag(self, tag):
        self.check_data_buffer()
        if self.__depth == self._dispatch_depth:
            self.dispatcher(self.min_dom)
        elif self.__depth > self._dispatch_depth:
            self._ptr = self._ptr.parent

        self.depth_dec()
        if self.__depth == 0:
            self.stream_footer_received()

    def handle_cdata(self, data):
        if self.data_buffer:
            self.data_buffer.append(data)
        else:
            self.data_buffer = [data]

    def handle_namespace_start(self):
        pass

    def destroy(self):
        self.check_data_buffer()
        self.parse.StartElementHandler = None
        self.parse.EndElementHandler = None
        self.parse.CharacterDataHandler = None
        self.parse.StartNamespaceDeclHandler = None

    def depth_inc(self):
        self.__depth = self.__depth + 1

    def depth_dec(self):
        self.__depth = self.__depth - 1

    def stream_footer_received(self):
        pass