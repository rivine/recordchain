from pprint import pprint
from concurrent.futures import ThreadPoolExecutor
from js9 import j
import time
from .UIDServer import UIDServer

# JSBASE = j.application.jsbase_get_class()
# import signal

BASE = j.servers.gedis._self_class_get()
JSConfigBase = j.tools.configmanager.base_class_configs

class UIDServerFactory(BASE,JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.servers.uidserver"
        JSConfigBase.__init__(self, UIDServer)


    def configure(self, instance="main", port=9901, addr="localhost", adminsecret="g007g", ssl=False, zdbport=9902, interactive=False,reset=False):
        """
        e.g.
        js9 j.servers.gedis.start()'  
        will be different name depending the implementation
        """
        data = {"port": port, "addr": addr, "adminsecret_": adminsecret, "ssl": ssl}
        data["zdbport"]=zdbport
        server = self._child_class(instance=instance, data=data, parent=self, interactive=interactive,reset=reset)
        return server

    def test(self):
        """
        js9 'j.servers.uidserver.test()'

        will start in tmux the server & then connect to it using redisclient

        """
        s=self.configure(reset=True)
        s.start()
        
        rr = self.client_get('test')
        r=rr.redis

        from IPython import embed;embed(colors='Linux')

