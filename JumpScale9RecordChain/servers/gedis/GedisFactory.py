
# from pprint import pprint as print

from js9 import j

from .GedisServer import GedisServer

JSConfigBase = j.tools.configmanager.base_class_configs


class GedisFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.servers.gedis"
        JSConfigBase.__init__(self, GedisServer)

    def baseclass_get(self):
        return self._child_class

    def _self_class_get(self):
        return GedisFactory

    def start(self, instance="main", background=False):
        server = self.get(instance)
        ssl = server.config.data['ssl']        
        
        if background:
            cmd = "js9 '%s.start(instance=\"%s\")'" % (
                self.__jslocation__, instance)
            j.tools.tmux.execute(cmd, session='main', window='gedis_%s'%instance,pane='main', session_reset=False, window_reset=True)
            res=j.sal.nettools.waitConnectionTest("localhost",int(server.config.data["port"]),timeoutTotal=1000)
            if res==False:
                raise RuntimeError("Could not start gedis server on port:%s"%int(server.config.data["port"]))
            cl=self.client_get(instance=instance)
            assert cl.redis.execute_command("PING") is True
            self.logger.info("gedis server '%s' started"%instance)
        else:
            server = self.get(instance, create=False)
            server.start()

    def configure(self, instance="main", port=8889, addr="localhost", secret="", ssl=False, interactive=False, start=False, background=True):
        """
        e.g.
        js9 j.servers.gedis.start()'  
        will be different name depending the implementation
        """
        data = {"port": port, "addr": addr, "adminsecret_": secret, "ssl": ssl}
        server = self._child_class(instance=instance, data=data, parent=self, interactive=interactive)
        #####7ossam
        # there was no session here also on tmux, happened second

        if start:
            self.start(instance=instance, background=background)
        # return server

    def client_get(self, instance):
        """
        will user server arguments to figure out how to get client, is easy for testing
        """
        server = self.get(instance=instance)
        # import ipdb; ipdb.set_trace()
        ssl = server.config.data['ssl']
        if not ssl:
            client = j.clients.gedis.configure(instance, ipaddr=server.config.data['addr'], port=int(server.config.data['port']), ssl= False)
        else:
            client = j.clients.gedis.configure(instance, ipaddr=server.config.data['addr'], port=int(server.config.data['port']),ssl=ssl, ssl_keyfile=None, ssl_certfile=server.ssl_cert_path)
        # import ipdb; ipdb.set_trace()
        # assert client.redis.execute_command("PING") == True
        return client
    
