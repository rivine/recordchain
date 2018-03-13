
from JumpScale9 import j

JSBASE = j.application.jsbase_get_class()


class SchemaProperty(JSBASE):
    def __init__(self):
        JSBASE.__init__(self)
        self.name = ""
        self.alias = ""
        self.default = ""
        self.js9type = None
        self.isList = False
        self.enumeration = []
        self.comment = ""
        self.pointer_type = None

    @property
    def default_as_python_code(self):
        return self.js9type.python_code_get(self.default)

    @property
    def js9_typelocation(self):
        return "j.data.types.%s" % self.js9type.NAME

    def __str__(self):
        if self.default not in [None,0,"",[]]:
            out = "prop:%-25s (%s)     default:%s"%(self.name,self.js9type.NAME,self.default)
        else:
            out = "prop:%-25s (%s)"%(self.name,self.js9type.NAME)
        return out
        
    __repr__ = __str__
