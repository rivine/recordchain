
# from pprint import pprint as print

from js9 import j

from .GedisServer import GedisServer
import os
JSConfigBase = j.tools.configmanager.base_class_configs

from .GedisServerExample import GedisServerExample

class GedisFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.servers.gedis"
        JSConfigBase.__init__(self, GedisServer)

    def baseclass_get(self):
        return self._child_class

    def _self_class_get(self):
        return GedisFactory

    def start(self, instance="main", background=False):
        server = self.get(instance,interactive=False)
        ssl = server.config.data['ssl']

        if background:
            cmd = "js9 '%s.start(instance=\"%s\")'" % (
                self.__jslocation__, instance)
            j.tools.tmux.execute(cmd, session='main', window='gedis_%s'%instance,pane='main', session_reset=False, window_reset=True)
            res=j.sal.nettools.waitConnectionTest("localhost",int(server.config.data["port"]),timeoutTotal=1000)
            if res==False:
                raise RuntimeError("Could not start gedis server on port:%s"%int(server.config.data["port"]))
            cl=self.client_get(instance=instance)
            assert cl.redis.execute_command("ping") == b"PONG"
            self.logger.info("gedis server '%s' started"%instance)
        else:
            server = self.get(instance, create=False)
            server.start()

    def configure(self, instance="main", port=8889, addr="localhost", secret="", ssl=False, interactive=False, classpaths=[], start=False, background=True):
        """
        e.g.
        js9 j.servers.gedis.start()'  
        will be different name depending the implementation
        """
        data = {"port": port, "addr": addr, "adminsecret_": secret, "ssl": ssl, "classpaths": classpaths}
        server = self._child_class(instance=instance, data=data, parent=self, interactive=interactive)

        if start:
            self.start(instance=instance, background=background)
        # return server

    def client_get(self, instance):
        """
        will user server arguments to figure out how to get client, is easy for testing
        """
        server = self.get(instance=instance,interactive=False)
        ssl = server.config.data['ssl']
        if not ssl:
            client = j.clients.gedis.configure(instance, ipaddr=server.config.data['addr'], port=int(server.config.data['port']), ssl= False)
        else:
            client = j.clients.gedis.configure(instance, ipaddr=server.config.data['addr'], port=int(server.config.data['port']),ssl=ssl, ssl_keyfile=None, ssl_certfile=server.ssl_cert_path)
        return client

    def test(self, dobenchmarks=True):
        """
        js9 'j.servers.gedis.test(dobenchmarks=False)'

        will start in tmux the server & then connect to it using redisclient

        """        
        classpath = j.sal.fs.getDirName(os.path.abspath(__file__)) +"GedisServerExample.py"

        server = self.configure(instance="test", port=5000, addr="127.0.0.1", secret="1234", ssl=False, \
            interactive=False, background=True, start=True)

        server.cmds_add("example",path=classpath)
        #OR:
        # server.cmds_add("example",class_=GedisServerExample)

        self._test(server, dobenchmarks=dobenchmarks)

    def _test(self, server, dobenchmarks=True):

        db = j.servers.zdb.configure(instance="test", adminsecret="1234", reset=True, mode="direct", id_enable=True)
        db.start()

        r = self.client_get('test')
        # assert True == r.ping()
        # is it binary or can it also return string
        ping1value = r.redis.execute_command("ping")
        
        print("TEST")
        from IPython import embed;embed(colors='Linux')        
    
