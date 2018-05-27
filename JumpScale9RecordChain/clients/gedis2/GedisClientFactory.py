
from pprint import pprint as print

from js9 import j

import sys

JSConfigBase = j.tools.configmanager.base_class_configs
from .GedisClient import GedisClient


class GedisClientFactory(JSConfigBase):
    """
    is nothing more for now than the redis_config client
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.gedis2"
        JSConfigBase.__init__(self, GedisClient)
        #PREPARE FOR CODE GENERATION
        self._template_engine = None    
        self._template_code_client = None
        self._code_model_template = None
        self.code_generation_dir = j.dirs.VARDIR+"/codegen/gedis_client/"
        j.sal.fs.createDir(self.code_generation_dir)
        if self.code_generation_dir not in sys.path:
            sys.path.append(self.code_generation_dir)
        j.sal.fs.touch(self.code_generation_dir+"/__init__.py")
        self.logger.debug("codegendir:%s" % self.code_generation_dir)        
        

    def configure(self, instance="core",ipaddr="localhost", \
            port=5000, password="", unixsocket="", 
            ssl=False, ssl_keyfile=None, ssl_certfile=None):

        """
        #TODO:*1 need to define well what this keyfile/certfile is
        """
        data = {}
        data["addr"] = ipaddr
        data["port"] = port
        data["password_"] = password
        data["unixsocket"] = unixsocket
        data["ssl"] = ssl
        if ssl_certfile:
            #check if its a path, if yes load
            data["ssl"] = True 
            data["sslkey"] = True #means path will be used for sslkey at redis client
            
        r = self.get(instance=instance, data=data)

        if ssl_certfile:
            #check if its a path, if yes safe the key paths into config
            r.ssl_keys_save(ssl_certfile)

        return r

    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__))


    @property
    def template_engine(self):
        if self._template_engine is None:
            from jinja2 import Environment, PackageLoader

            self._template_engine = Environment(
                loader=PackageLoader('JumpScale9RecordChain.clients.gedis2', 'templates'),
                trim_blocks=True,
                lstrip_blocks=True,
            )
        return self._template_engine

    @property
    def code_client_template(self):
        if self._template_code_client == None:
            self._template_code_client = self.template_engine.get_template("template.py")
        return self._template_code_client

    @property
    def code_model_template(self):
        if self._code_model_template == None:
            self._code_model_template = self.template_engine.get_template("ModelBase.py")
        return self._code_model_template


    def test(self, dobenchmarks=True):
        """
        js9 'j.clients.gedis2.test()'

        """      

        #FOR CURRENT TEST TO MAKE SURE WE START FROM NOTHING
        j.sal.fs.remove(self.code_generation_dir)
        j.sal.fs.createDir(self.code_generation_dir)

        self.configure(instance="test",ipaddr="localhost", \
            port=5000, password="", unixsocket="", 
            ssl=False, ssl_keyfile=None, ssl_certfile=None)

        cl = self.get("test")

        o=cl.models.test_gedis2_cmd1.new()
        o.cmd.name="aname"
        o.cmd2.name="aname2"
        o2=cl.models.test_gedis2_cmd1.set(o)
        o3=cl.models.test_gedis2_cmd1.set(o2) #make sure id stays same

        assert o2.id==o3.id

        o4=cl.models.test_gedis2_cmd1.get(o3.id)

        o3.ddict==o4.ddict

        from IPython import embed;embed(colors='Linux')


        #LOW LEVEL AT THIS TIME BUT TO SHOW SOMETHING
        cmds_meta =r.redis.execute_command("system.api_meta")

        cmds_meta = j.data.serializer.msgpack.loads(cmds_meta)
        for namespace,capnpbin in cmds_meta.items():
            cmds_meta[namespace] = GedisCmds(namespace=namespace,capnpbin=capnpbin)

        #this will make sure we have all the local schemas
        schemas_meta =r.redis.execute_command("system.core_schemas_get")
        schemas_meta = j.data.serializer.msgpack.loads(schemas_meta)
        for key,txt in schemas_meta.items():
            if key not in j.data.schema.schemas:
                j.data.schema.schema_from_text(txt,url=key)


        s=j.data.schema.schema_from_url('jumpscale.gedis2.example.system.test.in')
        o=s.new()
        o.name = "aname"
        o.nr = 1

        res = r.redis.execute_command("system.test",o.data)

        s=j.data.schema.schema_from_url('jumpscale.gedis2.example.system.test.out')
        o2=s.get(capnpbin=res)

        assert o.name == o2.name
        

        from IPython import embed;embed(colors='Linux')        
    
        