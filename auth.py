__author__ = 'Administrator'

from utils import Plugin


class SASL(Plugin):
    def __init__(self, username, password):
        super(Plugin, self).__init__()