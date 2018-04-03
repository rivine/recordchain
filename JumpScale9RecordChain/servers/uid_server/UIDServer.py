
from JumpScale9 import j
# import struct

ServerClass = j.servers.gedis.baseclass_get()

TEMPLATE = """
addr = "localhost"
port = "9901"
ssl = false
adminsecret_ = ""
zdbport = 9902
"""
class UIDServer(ServerClass):
    def __init__(self,instance, data={}, parent=None, interactive=False, reset=False):
        ServerClass.__init__(self, instance=instance, data=data,
                              parent=parent, interactive=interactive, template=TEMPLATE)      

        d=self.config.data

        s= j.servers.zdb.configure(instance="uid_db",port=d["zdbport"],mode="user",reset=reset,adminsecret=d["adminsecret_"],start=True,id_enable=False)
        for ns in ["user","group","schema","uid"]:
            if j.clients.zdb.exists("uids_%s"%ns) is False or reset:
                j.clients.zdb.configure(instance="uids_%s"%ns, namespace=ns, secret=d["adminsecret_"], \
                    port=d["zdbport"], adminsecret=d["adminsecret_"], mode="user", id_enable=False, started=True)

        for ns in ["user","group","schema","uid"]:
            self.__dict__["db_%s" % ns]=j.clients.zdb.get(instance="uids_%s"%ns)

        from IPython import embed;embed(colors='Linux')

    def ping_cmd(self, request):
        return "ping"


    def start(self):

        
        
        return ServerClass.start(self)