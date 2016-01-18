__author__ = 'Administrator'


class Plugin(object):
    def __init__(self):
        self.owner = None
        self.owner_old_method = []
        self.export_method = []

    def Plugin(self, owner):
        self.owner = owner
        for method in self.export_method:
            if owner.__dict__.has_key(method.__name__):
                self.owner_old_method.append(owner.__dict__[method.__name__])

            owner.__dict__[method.__name__] = method

        owner.__dict__[self.__class__.__name__] = self
        if self.__class__.__dict__.has_key("plugin"):
            self.plugin(owner)

    def Plugout(self):
        ret = None
        if self.__class__.__dict__.has_key("plugout"):
            ret = self.plugout()

        for method in self.export_method:
            del self.owner.__dict__[method.__name__]
        for method in self.owner_old_method:
            self.owner.__dict__[method.__name__] = method
        del self.owner.__dict__[self.__class__.__name__]
        return ret
