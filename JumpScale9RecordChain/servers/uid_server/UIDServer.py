

from JumpScale9 import j

JSBASE = j.application.jsbase_get_class()


ServerClass = j.servers.gedis.get_base_class()


def ping(request):
    return "PONG"


class UIDServer(ServerClass):
    def __init__(self,host='localhost', port=9999):
        ServerClass.__init__(self, host=host, port=port)
        self.register_command('PING', ping)

    def testb(self, request):
        return b"testworked"

    def test(self, request):
        return "testworked"


    def error(self, request):
        raise RuntimeError("error")
