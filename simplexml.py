__author__ = 'Administrator'
import xml.parsers.expat


class Node:
    def __init__(self, tag, attrs={}, namespace=""):
        self.tag = tag
        self.attrs = attrs
        self.namespace = namespace
        self.kids = []
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
            pass

        return s


class NodeBuilt:
    def __init__(self):
        self._dispatch_depth = 1
        self.__depth = 0
        self.parse = xml.parsers.expat.ParserCreate()