from pprint import pprint
from concurrent.futures import ThreadPoolExecutor
from js9 import j
import time
from .UIDServer import UIDServer

JSBASE = j.application.jsbase_get_class()
import signal

class UIDServerFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.servers.uidserver"
        JSBASE.__init__(self)

    def get(self):
        return UIDServer()

    def configure(self,adminsecret="1234tf",secret="1234",reset=True,start=True):
        """
        js9 'j.servers.uidserver.configure()'
        """ 
        if start:        
            j.servers.zdb.configure(instance="uid_db",port=9902,mode="user",reset=reset,adminsecret=adminsecret)
            s=j.servers.zdb.get(instance="uid_db")
            s.start()
        for ns in ["user","group","schema","uid"]:
            j.clients.zdb.configure(instance="uids_%s"%ns, namespace=ns, secret=secret, port=9902, adminsecret=adminsecret, mode="user", id_enable=False)
        if start:
            self.start()

    def start(self,background=True):
        """
        js9 'j.servers.uidserver.start()'
        """
        if background:
            j.servers.zdb.start(instance="uid_db")                        
            cmd = "js9 'j.servers.uidserver.start(background=False)'"
            j.tools.tmux.execute(cmd, session='main', window='uidserver',pane='main', session_reset=False, window_reset=True)
            self.logger.info("waiting for uidserver to start on port 9901")
            res = j.sal.nettools.waitConnectionTest("localhost",9901)
            if res is False:
                raise RuntimeError("could not start uidserver: localhost:9901")
            self.logger.info("UID SERVER STARTED ON :%s"%9901)

        else:
            s = UIDServer(port=9901)
            s.start()


    def test(self):
        """
        js9 'j.servers.uidserver.test()'

        will start in tmux the server & then connect to it using redisclient

        """
        self.configure()
        
        r = j.clients.gedis.configure(instance='uidserver', ipaddr='localhost', port=9901).redis

        # r = j.clients.redis.get(port=9999)

        from IPython import embed;embed(colors='Linux')

