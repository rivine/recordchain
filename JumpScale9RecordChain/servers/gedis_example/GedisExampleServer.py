
from JumpScale9 import j
import struct

JSBASE = j.application.jsbase_get_class()
ServerClass = j.servers.gedis.get_base_class()




class GedisExampleServer(ServerClass):
    def __init__(self,host='127.0.0.1', port=8889):
        ServerClass.__init__(self, host=host, port=port)

        self.zdbconn = j.clients.redis.get(port=8888, set_patch=True) # default port for 0-db
        self.mindb = {}
        

    def ping_cmd(self,request):
        return "PONG"

    def testb_cmd(self, request):
        return "testworked"

    def testa_cmd(self, request):
        return "testworked"

    def setf_cmd(self, request):
        k, v = request[1], request[2]
        self.mindb[k] = v
        return k

    def incrf_cmd(self, request):
        k = request[1]
        try:
            self.mindb[k] = int(self.mindb.get(k, 0)) + 1
        except:
            raise ValueError("Value isn't an integer: {}".format(self.mindb[k]))
        return self.mindb[k]


    def getf_cmd(self, request):
        k = request[1]
        return self.mindb.get(k, None)


    def set_cmd(self, request):
        k, v = request[1], request[2]
        res = self.zdbconn.execute_command("SET", k, v)

        return res

    def get_cmd(self, request):
        k = request[1]
        res = self.zdbconn.execute_command("GET", k)
        return res

    def error_cmd(self, request):
        raise RuntimeError("error")
