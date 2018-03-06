

from JumpScale9 import j

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

    def testb(self, request):
        return "testworked"

    def testa(self, request):
        return "testworked"


    def error(self, request):
        raise RuntimeError("error")
