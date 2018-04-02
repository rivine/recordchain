
from JumpScale9 import j
# import struct

ServerClass = j.servers.gedis.baseclass_get()

class UIDServer(ServerClass):
    def __init__(self,instance, data={}, parent=None, interactive=False):
        ServerClass.__init__(self, instance=instance, data=data,
                              parent=parent, interactive=interactive)        


        for ns in ["user","group","schema","uid"]:
            self.__dict__["db_%s" % ns]=j.clients.zdb.get(instance="uids_%s"%ns)

        from IPython import embed;embed(colors='Linux')

    def ping_cmd(self, request):
        return "ping"


