
from JumpScale9 import j

JSBASE = j.application.jsbase_get_class()


class SchemaProperty(JSBASE):
    def __init__(self):
        JSBASE.__init__(self)
        self.name = ""
        self.default = ""
        self.js9type = None
        self.enumeration = []
