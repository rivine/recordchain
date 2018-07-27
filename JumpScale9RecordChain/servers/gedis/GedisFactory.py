import os

from js9 import j

from .GedisServer import GedisServer
from .GedisCmds import GedisCmds
from .GedisChatBot import GedisChatBotFactory

JSConfigBase = j.tools.configmanager.base_class_configs


class GedisFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.servers.gedis"

        JSConfigBase.__init__(self, GedisServer)

        self._template_engine = None
        self._template_code_server = None
        self._code_model_template = None
        self._code_start_template = None
        self._code_test_template = None
        self._js_client_template = None

    def get(self,instance='main',data={},interactive = False):

        return super(GedisFactory, self).get(instance=instance, data=data, interactive=interactive)

    def chatbot_test(self):
        """
        js9 'j.servers.gedis.chatbot_test()'
        """
        bot = GedisChatBotFactory()
        bot.test()



    def new(
            self,
            instance="test",
            port=8889,
            host="localhost",
            app_dir="",
            ssl=False,
            websockets_port=9901,
            secret = "",
            zdb_instance = "",
            path = "",
            reset = False
        ):
        """
        creates new server on path, if not specified will be current path
        will start from example app

        js9 'j.servers.gedis.new(path="{{DIRS.TMPDIR}}/jumpscale/gedisapp/",reset=True)'

        """
        
        if path == "":
            path = j.sal.fs.getcwd()
        else:
            path = j.tools.jinja2.text_render(path)

        if reset:
            j.sal.fs.removeDirTree(path)

        if j.sal.fs.exists("%s/actors"%path) or j.sal.fs.exists("%s/schema"%path):
            raise RuntimeError("cannot do new app because app or schema dir does exist.")  

        
        src = j.clients.git.getContentPathFromURLorPath("https://github.com/rivine/recordchain/tree/development/apps/template")
        dest = path
        self.logger.info("copy templates to:%s"%dest)

        gedis = self.configure(instance=instance,port=port,host=host,app_dir=path,ssl=ssl,\
            websockets_port=websockets_port,secret = "",zdb_instance=zdb_instance)

        j.tools.jinja2.copy_dir_render(src,dest,reset=reset, j=j,name="aname", config=gedis.config.data, instance=instance)     

        self.logger.info("gedis app now in: '%s'\n    do:\n    cd %s;sh start.sh"%(dest,dest))   


    def geventservers_get(self,instance=""):
        """
        return (redis_server,websocket_server)
        """
        server = self.get(instance=instance)
        # res.append(server.websocket_server)
        return (server.redis_server,server.websocket_server)
 

    def configure(
            self,
            instance="test",
            port=8889,
            host="localhost",
            app_dir="",
            ssl=False,
            websockets_port=9901,
            secret = "",
            zdb_instance = "",
            interactive = False,
            configureclient = True
        ):

        if app_dir == "":
            app_dir = j.sal.fs.getcwd()
            

        data = {
            "port": str(port),
            "host": host,
            "adminsecret_": secret,
            "app_dir":app_dir,
            "ssl": ssl,
            "websockets_port" :str(websockets_port),
            "zdb_instance" :zdb_instance
        }

        if configureclient:
            j.clients.gedis.configure(instance=instance,
                host=host,port=port,secret=secret,ssl=ssl,reset=True,get=False)

        return self.get(instance, data,interactive=interactive)

    def cmds_get(self,namespace,capnpbin):
        """
        Used in client only
        """
        return GedisCmds(namespace=namespace,capnpbin=capnpbin)

    @property
    def path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__))

    def test(self,zdb_start=True):
        """
        js9 'j.servers.gedis.test(zdb_start=False)'
        """

        #remove configuration of the gedis factory
        self.delete("test")

        if zdb_start:
            cl = j.clients.zdb.testdb_server_start_client_get(start=zdb_start)  #starts & resets a zdb in seq mode with name test       

        dest =  j.clients.git.getContentPathFromURLorPath("https://github.com/rivine/recordchain/tree/development/apps/example")
        gedis = self.configure(instance="test",port=8888,host="localhost",app_dir=dest,ssl=False,\
            zdb_instance = "test",
            websockets_port=9999,secret = "1234",
            interactive=False)

        #we need to run multiple servers, lets get a rack for gevent
        rack=j.servers.gevent_servers_racks.get()

        rack.add(j.servers.gedis.geventserver_get("test"))
    

        from IPython import embed;embed(colors='Linux')





    # @property
    # def code_server_template(self):
    #     if self._template_code_server is None:
    #         self._template_code_server = self.template_engine.get_template("template.py")
    #     return self._template_code_server

    # @property
    # def code_model_template(self):
    #     if self._code_model_template is None:
    #         self._code_model_template = self.template_engine.get_template("ModelBase.py")
    #     return self._code_model_template

    # @property
    # def js_client_template(self):
    #     if self._js_client_template is None:
    #         self._js_client_template = self.template_engine.get_template("client.js")
    #     return self._js_client_template

    # @property
    # def code_start_template(self):
    #     if self._code_start_template is None:
    #         self._code_start_template = self.template_engine.get_template("start.py")
    #     return self._code_start_template

    # @property
    # def code_test_template(self):
    #     if self._code_test_template is None:
    #         self._code_test_template = self.template_engine.get_template("test.py")
    #     return self._code_test_template
