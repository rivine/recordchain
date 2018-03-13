
from JumpScale9 import j
import struct

JSBASE = j.application.jsbase_get_class()
ServerClass = j.servers.gedis.get_base_class()



class UIDServer(ServerClass):
    def __init__(self,host='127.0.0.1', port=9901):
        ServerClass.__init__(self, host=host, port=port)

        

    def ping_cmd(self, request):
        return "ping"


