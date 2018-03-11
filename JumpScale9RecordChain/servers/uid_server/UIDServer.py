
from JumpScale9 import j
import struct

JSBASE = j.application.jsbase_get_class()
ServerClass = j.servers.gedis.get_base_class()


def ping(request):
    return "PONG"



class UIDServer(ServerClass):
    def __init__(self,host='127.0.0.1', port=9999):
        ServerClass.__init__(self, host=host, port=port)
        self.register_command('PING', ping)
        self.register_command('TESTA', self.testa)
        self.register_command('TESTB', self.testb)
        self.register_command("SETF", self.setf_cmd)
        self.register_command("GETF", self.getf_cmd)
        self.zdbconn = j.clients.redis.get(port=9900) # default port for 0-db

    def testb(self, request):
        return "testworked"

    def testa(self, request):
        return "testworked"

    def setf_cmd(self, request):
        # FIXME: proxying set commands to 0-db gives lots of problems
        # FOR NOW it's a workaround against the sent values.
        k, v = request[1], request[2]
        # print("** IN SETA CMD => k {} , {}, v {} , {} ".format(k, type(k), v, type(v)))
        res = self.zdbconn.execute_command("SET ", k.decode(), v.decode())
        # print("** IN SETA CMD: RES {} , type(res) : {} ".format(res, type(res)))

        return res

    def getf_cmd(self, request):
        k = request[1]
        # print("** IN GETA CMD => k {} , {}".format(k, type(k)))
        res = self.zdbconn.execute_command("GET", k)
        # print("** IN GETA CMD: RES {} , {} ".format(res, type(res)))
        return res

    def error(self, request):
        raise RuntimeError("error")
