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
        cmd = "js9 'j.servers.uidserver.start()'"
        j.tools.tmux.execute(cmd, session='main', window='uidserver',pane='main', session_reset=False, window_reset=True)

        redis_client = j.clients.redis_config.get_by_params(
            instance='uidserver', ipaddr='localhost', port=9999, password='', unixsocket='', ardb_patch=False, set_patch=True)
        r = redis_client.redis
        # r = j.clients.redis.get(port=9999)

        self.logger.info("Started test2")
        # assert True == r.ping()
        assert r.execute_command("PING") == True #is it binary or can it also return string
        assert r.execute_command("TESTB") == b'testworked'
        assert r.execute_command("TESTA") == b'testworked'
        self.logger.info("First assersions passed")
        try:
            for i in range(100):
                k = r.execute_command("SET", "a{}".format(i), "dmdm")
                # self.logger.info("NEW KEY: {}".format(k))
                value = r.execute_command("GET", k)
                # print("VAL: ", value)
                assert value == b"dmdm"
        except Exception as e:
            print("ERROR: ", e)
        self.logger.info("Batch assertions done")
        
        self.logger.info("[+]Test passed")

        #PERFORMANCE TEST
        def perf_test():
            futures = []
            MAX_NUM = 200000
            start = now()
            self.logger.info("Started benching with {}".format(MAX_NUM))
            with ThreadPoolExecutor(max_workers=4) as executor:
                for i in range(MAX_NUM):
                    future = executor.submit(r.execute_command, "SET", b"AKEY", b"AVALUE")
                    futures.append(future)
            
            self.logger.debug("FUTURES LEN: ", len(futures))
            ## ASSERT ALL DONE
            while not all([f.done() for f in futures]):
                continue

            delta = now() - start          
            donefutures_len = len(futures)
            self.logger.debug("DONE COMMANDS {} in {} seconds  =>  {} command/second".format( donefutures_len, delta, donefutures_len/int(delta)))
            return int(donefutures_len / delta)

        def bench(times=5):
            return sum([perf_test() for i in range(times)]) / times

        if dobenchmarks:
            # * [+]Average: 3883.2 commands/second
            self.logger.info("[+]Average: {} commands/second".format(bench())) 


    def test3(self, dobenchmarks=True):
        """
        js9 'j.servers.uidserver.test()'

        will start in tmux the server & then connect to it using redisclient

        """
        cmd = "js9 'j.servers.uidserver.start()'"
        j.tools.tmux.execute(cmd, session='main', window='uidserver',pane='main', session_reset=False, window_reset=True)

        redis_client = j.clients.redis_config.get_by_params(
            instance='uidserver', ipaddr='localhost', port=9999, password='', unixsocket='', ardb_patch=False, set_patch=True)
        r = redis_client.redis

        self.logger.info("[+]Test passed")

        #PERFORMANCE TEST
        def perf_test():
            futures = []
            MAX_NUM = 200000
            start = now()
            self.logger.info("Started benching INCR with {}".format(MAX_NUM))
            r.execute_command("SETF", b"AKEY", b"1")
            with ThreadPoolExecutor(max_workers=4) as executor:
                for i in range(MAX_NUM):
                    future = executor.submit(r.execute_command, "INCRF", b"AKEY")
                    futures.append(future)
            
            self.logger.debug("FUTURES LEN: ", len(futures))
            ## ASSERT ALL DONE
            while not all([f.done() for f in futures]):
                continue

            delta = now() - start          
            donefutures_len = len(futures)
            self.logger.debug("DONE COMMANDS {} in {} seconds  =>  {} command/second".format( donefutures_len, delta, donefutures_len/int(delta)))
            print(r.execute_command("GETF", b"AKEY", b"1"))

            return int(donefutures_len / delta)

        def bench(times=5):
            return sum([perf_test() for i in range(times)]) / times

        if dobenchmarks:
            #* [+]Average: 7992.6 commands/second
            self.logger.info("[+]Average: {} commands/second".format(bench()))
