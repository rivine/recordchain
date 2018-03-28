
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
        
        if background:
            cmd = "js9 '%s.start(instance=\"%s\",background=False)'" % (
                self.__jslocation__, instance)
            j.tools.tmux.execute(cmd, session='main', window='gedis',
                                 pane='main', session_reset=False, window_reset=True)
            j.sal.nettools.checkListenPort(int(server.config.data["port"]))
        else:
            server = self.get(instance, create=False)
            server.start()

    def configure(self, instance="main", port=8889, addr="localhost", secret="", ssl=False, interactive=False, start=False, background=False):
        """
        e.g.
        js9 j.servers.gedis.start()'  
        will be different name depending the implementation
        """
        data = {"port": port, "addr": addr, "adminsecret_": secret, "ssl": ssl}
        server = self._child_class(
            instance=instance, data=data, parent=self, interactive=interactive)
        if start:
            self.start(instance=instance, background=background)
        return server

    def client_get(self, instance):
        """
        will user server arguments to figure out how to get client, is easy for testing
        """
        server = self.get(instance=instance)
        ssl = server.config.data['ssl']
        if not ssl:
            cli = j.clients.gedis.configure(instance, ipaddr=server.config.data['addr'], port=int(server.config.data['port']), ssl= False)
        else:
            cli = j.clients.gedis.configure(instance, ipaddr=server.config.data['addr'], port=int(server.config.data['port']),
                                            ssl=ssl, ssl_keyfile=server.ssl_priv_key_path, ssl_certfile=server.ssl_cert_path)
        self.get(instance)
        return cli
    
