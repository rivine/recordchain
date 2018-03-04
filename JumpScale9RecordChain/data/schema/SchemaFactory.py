
from JumpScale9 import j

JSBASE = j.application.jsbase_get_class()

from .Schema import *

class SchemaFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.data.schema"
        JSBASE.__init__(self)

    def schema_from_text(self,txt):
        return Schema(txt=txt)


    def test(self):
        schema = """
        @url = despiegk.test
        nr = 0
        date_start = 0 (D)
        description = ""
        token_price = " USD"
        cost_estimate:hw_cost = 0.0
        U = 0.0
        pool_type = "managed,unmanaged" (E)
        """