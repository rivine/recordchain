printf = print
from pprint import pprint as print
from concurrent.futures import ThreadPoolExecutor
from js9 import j
import time
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
        # import ipdb;ipdb.set_trace()
        j.tools.tmux.execute(cmd, session='main', window='uidserver',pane='main', session_reset=False, window_reset=True)

        # redis_client = j.clients.redis_config.get_by_params(
        #     instance='uidserver', ipaddr='localhost', port=9999, password='', unixsocket='', ardb_patch=False)
        # r = redis_client.redis
        r = j.clients.redis.get(port=9999)

        # assert True == r.ping()
        assert r.execute_command("PING") == True #is it binary or can it also return string
        assert r.execute_command("TESTB") == b'testworked'
        assert r.execute_command("TESTA") == b'testworked'

        error=False
        try:
            r.execute_command("ERROR") #should raise error
        except Exception as e:
            error=True
        assert error
        printf("Test passed")
        
        #PERFORMANCE TEST
        #NEED TO ACHIEVE +500 rec/sec

        futures = []
    
        start = time.time()
        printf("Started benching..")
        with ThreadPoolExecutor(max_workers=4) as executor:
            for i in range(100000):
                future = executor.submit(r.execute_command, "TESTA")
                delta = time.time() - start
                if int(delta) >= 5:
                    break
                futures.append(future)
        
        donefutures = [x for x in futures if x.done()]
        printf("DONE COMMANDS IN 1 SEC: ", len(donefutures)/int(delta))


        # from IPython import embed;embed(colors='Linux')