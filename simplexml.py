__author__ = 'Administrator'
import xml.parsers.expat


class Node:
    def __init__(self, tag, attrs={}, namespace=""):
        self.tag = tag
        self.attrs = attrs
        self.namespace = namespace
        self.kids = []
        self.parent = None
        self.name = ""

        if tag:
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
                    s = s + " xmlns=%s" % self.namespace

        for key in self.attrs:
            s = s + " %s=%s" %(key, self.attrs[key])

        if self.kids:
            pass

        if not self.kids and s.endswith(">"):
            s = s[:-1]+"/>"
        else:
            s = s + "<"+self.name+"/>"

        return s


class NodeBuilt:
    def __init__(self):
        self._dispatch_depth = 1
        self.__depth = 0
        self.parse = xml.parsers.expat.ParserCreate()