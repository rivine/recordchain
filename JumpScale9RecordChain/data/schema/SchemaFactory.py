
from JumpScale9 import j

JSBASE = j.application.jsbase_get_class()

from .Schema import *
from .List0 import List0
import sys


class SchemaFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.data.schema"
        JSBASE.__init__(self)
        self._template_engine = None
        self.code_generation_dir = j.dirs.VARDIR+"/codegen/schema/"
        j.sal.fs.createDir(self.code_generation_dir)
        if self.code_generation_dir not in sys.path:
            sys.path.append(self.code_generation_dir)
        j.sal.fs.touch(self.code_generation_dir+"/__init__.py")
        self.logger.debug("codegendir:%s" % self.code_generation_dir)
        self.db = j.clients.redis.core_get()
        self.schemas = {}

    def reset(self):
        self.schemas = {}

    def schema_from_text(self, txt):
        s = Schema(text=txt)
        if s.url is not "":
            self.schemas[s.url] = s
        return s

    def schema_add(self, txt):
        """
        add schema text (can be multile blocks starting with @) to this class
        result schema's can be found from self.schema_from_url(...)
        """
        block = ""
        state = "start"
        res=[]
        for line in txt.split("\n"):

            l=line.lower().strip()

            if block=="":
                if l == "" or l.startswith("#"):
                    continue

            if l.startswith("@url"):
                if block is not "":
                    res.append(self.schema_from_text(block))
                block = ""

            block += "%s\n" % line

        if block != "":
            res.append(self.schema_from_text(block))

        return res

    def schema_from_url(self, url):
        """
        url e.g. despiegk.test
        """
        url = url.lower().strip()
        if url in self.schemas:
            return self.schemas[url]
        # schema_txt = self.db.get("schemas:%s"%url)
        # if schema_txt == None:
        else:
            raise RuntimeError("could not find schema with url:%s" % url)
        # s = self.schema_from_text(schema_txt)
        # return s

    @property
    def template_engine(self):
        if self._template_engine is None:
            from jinja2 import Environment, PackageLoader

            self._template_engine = Environment(
                loader=PackageLoader(
                    'JumpScale9RecordChain.data.schema', 'templates'),
                trim_blocks=True,
                lstrip_blocks=True,
            )
        return self._template_engine

    def list_base_class_get(self):
        return List0

    def test(self):
        """
        js9 'j.data.schema.test()'
        """
        self.test1()
        self.test2()
        self.test3()

    def test1(self):
        """
        js9 'j.data.schema.test1()'
        """
        schema = """
        @url = despiegk.test
        @name = TestObj
        llist2 = "" (LS)        
        nr = 4
        date_start = 0 (D)
        description = ""
        token_price = "10 USD" (N)
        cost_estimate:hw_cost = 0.0 #this is a comment
        llist = []
        llist3 = "1,2,3" (LF)
        llist4 = "1,2,3" (L)
        llist5 = "1,2,3" (LI)
        U = 0.0
        #pool_type = "managed,unmanaged" (E)  #NOT DONE FOR NOW
        """

        s = j.data.schema.schema_from_text(schema)
        print(s)

        o = s.get()

        o.llist.append(1)
        o.llist2.append("yes")
        o.llist2.append("no")
        o.llist3.append(1.2)
        o.llist4.append(1)
        o.llist5.append(1)
        o.llist5.append(2)
        o.U = 1.1
        o.nr = 1
        o.token_price = "10 EUR"
        o.description = "something"

        o.cobj

        schema = """
        @url = despiegk.test2
        @name = TestObj
        llist2 = "" (LS)        
        nr = 4
        date_start = 0 (D)
        description = ""
        token_price = "10 USD" (N)
        cost_estimate:hw_cost = 0.0 #this is a comment
        llist = []

        @url = despiegk.test3
        @name = TestObj2
        llist = []
        description = ""
        """
        j.data.schema.schema_add(schema)
        s1 = self.schema_from_url("despiegk.test2")
        s2 = self.schema_from_url("despiegk.test3")

        o1 = s1.get()
        o2 = s2.get()
        o2.llist.append("1")

        print("TEST 1 OK")

    def test2(self):
        """
        js9 'j.data.schema.test2()'
        """
        schema0 = """
        @url = despiegk.test.group
        @name = Group
        description = ""
        llist = "" (LO) !despiegk.test.users
        listnum = "" (LI)
        """

        schema1 = """
        @url = despiegk.test.users
        @name = User
        nr = 4
        date_start = 0 (D)
        description = ""
        token_price = "10 USD" (N)
        cost_estimate:hw_cost = 0.0 (N) #this is a comment
        """

        s1 = self.schema_from_text(schema1)
        s0 = self.schema_from_text(schema0)

        print(s0)
        o = s1.get()

        print(s1.capnp_schema)
        print(s0.capnp_schema)

        print("TEST 2 OK")


    def test3(self):
        """
        js9 'j.data.schema.test3()'

        simple embedded schema

        """
        SCHEMA = """
        @url = jumpscale.gedis.cmd
        @name = GedisCmd
        name = ""
        comment = ""
        schemacode = ""

        @url = jumpscale.gedis.serverschema
        @name = GedisServerSchema
        cmds = (LO) !jumpscale.gedis.cmd

        @url = jumpscale.gedis.cmd1
        @name = GedisServerCmd1
        cmd = (O) !jumpscale.gedis.cmd
        cmd2 = (O) !jumpscale.gedis.cmd
        
        """
        self.schema_add(SCHEMA)
        s1 = self.schema_from_url("jumpscale.gedis.cmd")
        s2 = self.schema_from_url("jumpscale.gedis.serverschema")
        s3 = self.schema_from_url("jumpscale.gedis.cmd1")

        o = s2.get()
        for i in range(4):
            oo = o.cmds.new()
            oo.name = "test%s"%i

        assert o.cmds[2].name=="test2" 
        o.cmds[2].name="testxx"
        assert o.cmds[2].name=="testxx" 

        bdata = o.data

        o2 = s2.get(capnpbin=bdata)

        assert o.ddict == o2.ddict

        print (o.data)

        o3 = s3.get()
        o3.cmd.name = "test"
        o3.cmd2.name = "test"
        assert o3.cmd.name == "test"
        assert o3.cmd2.name == "test"

        bdata = o3.data
        o4 = s3.get(capnpbin=bdata)
        assert o4.ddict == o3.ddict

        assert o3.data == o4.data

        print("TEST 3 OK")


    # def test_list(self):
    #     """
    #     js9 'j.data.schema.test_list()'
    #     """

    #     lc = self.list_base_class_get()
    #     l = lc()
    #     for i in range(100):
    #         l.append(i)

    #     from IPython import embed
    #     embed(colors='Linux')
