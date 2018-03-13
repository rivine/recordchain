from pprint import pprint
from concurrent.futures import ThreadPoolExecutor
from js9 import j
import time
from .UIDServer import UIDServer
now = lambda: time.time()

JSBASE = j.application.jsbase_get_class()
import signal

class UIDServerFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.servers.uidserver"
        JSBASE.__init__(self)

    def get(self):
        return UIDServer()

    def configure(self,adminsecret="1234tf",secret="1234",reset=True):
        j.servers.zdb.start(instance="uid_db",port=9902,mode="user",reset=reset)
        for ns in ["user","group","schema"]:
            j.clients.zdb.get_by_params(instance="uids_%s"%ns, namespace=ns, secret=secret, port=9902, adminsecret=adminsecret, mode="user", id_enable=False)

    def start(self,background=True):
        """
        js9 'j.servers.uidserver.start()'
        """
        if background:
            j.servers.zdb.start(instance="uid_db",port=9902,mode="user",reset=False)
            cmd = "js9 'j.servers.uidserver.start(background=False)'"
            j.tools.tmux.execute(cmd, session='main', window='uidserver',pane='main', session_reset=False, window_reset=True)
            j.sal.nettools.waitConnectionTest("localhost",9901)
        else:
            s = GedisExampleServer(port=9901)
            s.start()


    def test(self):
        """
        js9 'j.servers.uidserver.test()'

        will start in tmux the server & then connect to it using redisclient

        """
