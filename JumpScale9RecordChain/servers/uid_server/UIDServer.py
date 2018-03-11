
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
        self.register_command("SET", self.set_cmd)
        self.register_command("GET", self.get_cmd)

        self.zdbconn = j.clients.redis.get(port=9900, set_patch=True) # default port for 0-db

    def testb(self, request):
        return "testworked"

    def testa(self, request):
        return "testworked"

    def set_cmd(self, request):
        k, v = request[1], request[2]
        res = self.zdbconn.execute_command("SET", k, v)

        return res

    def get_cmd(self, request):
        k = request[1]
        res = self.zdbconn.execute_command("GET", k)
        return res

    def error(self, request):
        raise RuntimeError("error")
