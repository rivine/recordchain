
from JumpScale9 import j
# import struct

JSBASE = j.application.jsbase_get_class()
ServerClass = j.servers.gedis.get_base_class()



class UIDServer(ServerClass):
    def __init__(self,host='127.0.0.1', port=9901):
        ServerClass.__init__(self, host=host, port=port)

        for ns in ["user","group","schema","uid"]:
            self.__dict__["db_%s" % ns]=j.clients.zdb.get(instance="uids_%s"%ns)

        from IPython import embed;embed(colors='Linux')

    def ping_cmd(self, request):
        return "ping"


