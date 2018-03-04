
from pprint import pprint as print

from js9 import j

from .UIDServer import UIDServer

JSBASE = j.application.jsbase_get_class()


class UIDServerFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.servers.uidserver"
        JSBASE.__init__(self)

    def get(self):
        return UIDServer()

    def start(self):
        """
        js9 'j.servers.uidserver.start()'
        """
        s = UIDServer()
        s.start()

    def test(self):
        """
        js9 'j.servers.uidserver.test()'

        will start in tmux the server & then connect to it using redisclient

        """
        cmd = "js9 'j.servers.uidserver.start()'"
        j.tools.tmux.execute(cmd, session='main', window='uidserver',pane='main', session_reset=False, window_reset=True)

        redis_client = j.clients.redis_config.get_by_params(
            instance='uidserver', ipaddr='localhost', port=9999, password='', unixsocket='', ardb_patch=False)
        r = redis_client.redis

        assert True == r.ping()
        assert r.execute_command("PING") == b'PONG' #is it binary or can it also return string
        # print(r.execute_command("TEST"))

        assert r.execute_command("TESTB") == b'testwork'
        assert r.execute_command("TEST") == b'testwork'

        error=False
        try:
            r.execute_command("ERROR") #should raise error
        except as Exception(e):
            error=True
        assert error

        #PERFORMANCE TEST
        #NEED TO ACHIEVE +500 rec/sec

        from IPython import embed;embed(colors='Linux')
