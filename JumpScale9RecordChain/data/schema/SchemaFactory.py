
from JumpScale9 import j

JSBASE = j.application.jsbase_get_class()

from .Schema import *
import sys

class SchemaFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.data.schema"
        JSBASE.__init__(self)
        self._template_engine = None
        self.code_generation_dir = j.dirs.VARDIR+"/codegeneration/"
        j.sal.fs.createDir(self.code_generation_dir)
        if self.code_generation_dir not in sys.path:
            sys.path.append(self.code_generation_dir)
        j.sal.fs.touch(self.code_generation_dir+"/__init__.py")
        self.logger.debug("codegendir:%s"%self.code_generation_dir)

    def schema_from_text(self,txt):
        return Schema(text=txt)

    @property
    def template_engine(self):
        if self._template_engine is None:
            from jinja2 import Environment, PackageLoader

            self._template_engine = Environment(
                loader=PackageLoader('JumpScale9RecordChain.data.schema', 'templates'),
                trim_blocks = True,
                lstrip_blocks = True,
            )
        return self._template_engine
        


    def test(self):
        """
        js9 'j.data.schema.test()'
        """
        schema = """
        @url = despiegk.test
        @name = TestObj
        nr = 4
        date_start = 0 (D)
        description = ""
        token_price = "10 USD" (N)
        cost_estimate:hw_cost = 0.0 #this is a comment
        llist = []
        llist2 = "1,2,3" (LS)
        llist3 = "1,2,3" (LF)
        llist4 = "1,2,3" (L)
        U = 0.0
        #pool_type = "managed,unmanaged" (E)  #NOT DONE FOR NOW
        """


        s = self.schema_from_text(schema)
        print(s)
        # s.code_generate()
        o=s.get()

        from IPython import embed;embed(colors='Linux')

    


