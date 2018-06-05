
# from pprint import pprint as print

from js9 import j
import time
from .GedisServer import GedisServer
from .GedisCmds import GedisCmds
import os
JSConfigBase = j.tools.configmanager.base_class_configs
import sys


class GedisFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.servers.gedis2"

        JSConfigBase.__init__(self, GedisServer)

        self._template_engine = None    
        self._template_code_server = None
        self._code_model_template = None
        path = os.path.join(j.dirs.VARDIR, 'codegen', 'gedis')
        if not j.sal.fs.exists(path):
            j.sal.fs.createDir(path)

        if not path in sys.path:
            sys.path.append(path)
        j.sal.fs.touch(os.path.join(path, '/__init__.py'))

        self.path = path

    def baseclass_get(self):
        return self._child_class

    def _self_class_get(self):
        return GedisFactory

    def start(self, instance="main", schema_path="", background=False, reset=False):
        server = self.get(instance,interactive=False)
        ssl = server.config.data['ssl']
        if background:
            cmd = "js9 '%s.start(instance=\"%s\", schema_path=\"%s\", reset=\"%s\")'" % (
                self.__jslocation__, instance, schema_path, reset)
            j.tools.tmux.execute(cmd, session='main', window='gedis_%s'%instance,pane='main', session_reset=False, window_reset=True)
            res=j.sal.nettools.waitConnectionTest("localhost",int(server.config.data["port"]),timeoutTotal=1000)
            if res==False:
                raise RuntimeError("Could not start gedis server on port:%s"%int(server.config.data["port"]))
            cl=self.client_get(instance=instance)
            # assert cl.redis.execute_command("system.ping") == b"PONG"
            self.logger.info("gedis server '%s' started"%instance)
        else:
            server = self.get(instance, create=False)
            server.start(schema_path=schema_path, reset=reset)

    def configure(self, instance="main", port=8889, addr="localhost", secret="", namespace="",ssl=False, path="", interactive=False, start=False, background=True):
        """
        e.g.
        js9 'j.servers.gedis2.start()'  
        will be different name depending the implementation
        """
        if path=="":
            path = j.sal.fs.getcwd()
        data = {"port": port, "addr": addr, "adminsecret_": secret, "ssl": ssl, "path":path, "namespace":namespace}
        server = self._child_class(instance=instance, data=data, parent=self, interactive=interactive)

        if start:
            self.start(instance=instance, background=background)
        return server

    def cmds_get(self,namespace,capnpbin):
        return GedisCmds(namespace=namespace,capnpbin=capnpbin)

    def client_get(self, instance):
        """
        e.g. j.servers.gedis2.client_get("test)
        will user server arguments to figure out how to get client, is easy for testing
        """
        server = self.get(instance=instance,interactive=False)
        ssl = server.config.data['ssl']
        if not ssl:
            client = j.clients.gedis2.configure(instance, ipaddr=server.config.data['addr'], port=int(server.config.data['port']), ssl= False)
        else:
            client = j.clients.gedis2.configure(instance, ipaddr=server.config.data['addr'], port=int(server.config.data['port']),ssl=ssl, ssl_keyfile=None, ssl_certfile=server.ssl_cert_path)
        return client

    @property
    def template_engine(self):
        if self._template_engine is None:
            from jinja2 import Environment, PackageLoader

            self._template_engine = Environment(
                loader=PackageLoader('JumpScale9RecordChain.servers.gedis2', 'templates'),
                trim_blocks=True,
                lstrip_blocks=True,
            )
        return self._template_engine

    @property
    def code_server_template(self):
        if self._template_code_server == None:
            self._template_code_server = self.template_engine.get_template("template.py")
        return self._template_code_server

    @property
    def code_model_template(self):
        if self._code_model_template == None:
            self._code_model_template = self.template_engine.get_template("ModelBase.py")
        return self._code_model_template        

    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__))


    def test(self, dobenchmarks=True,reset=False):
        """
        js9 'j.servers.gedis2.test(dobenchmarks=False)'

        will start in tmux the server & then connect to it using redisclient

        """

        if reset:
            j.sal.fs.remove("%s/codegen/"%j.dirs.VARDIR)
            bcdb=j.data.bcdb.get("test")  #has been set on start.py, will delete it here
            bcdb.destroy()
            j.tools.tmux.killall()

        classpath = j.sal.fs.getDirName(os.path.abspath(__file__)) +"EXAMPLE"

        self.start(instance="test", schema_path=classpath, background=True)

        r = self.client_get('test')

        ping1value = r.system.ping()
        assert ping1value == b'PONG'
        ping1value = r.system.ping_bool()
        assert ping1value == True

        #LOW LEVEL AT THIS TIME BUT TO SHOW SOMETHING
        cmds_meta =r.system.api_meta()

        cmds_meta = j.data.serializer.msgpack.loads(cmds_meta)
        for namespace,capnpbin in cmds_meta["cmds"].items():
            cmds_meta[namespace] = GedisCmds(namespace=namespace,capnpbin=capnpbin)

        
        # j.clients.gedis2.test()

        s= j.data.schema.schema_from_url('jumpscale.gedis2.example.system.test.in')
        o = s.new()
        o.name = "aname"
        o.nr = 1

        res = r.system.test("aname", 1)

        s=j.data.schema.schema_from_url('jumpscale.gedis2.example.system.test.out')

        o2=s.get(capnpbin=res.data)

        assert o.name == o2.name

        res = r.system.test_nontyped("name",10)
        assert j.data.serializer.json.loads(res) == ['name', 10]



