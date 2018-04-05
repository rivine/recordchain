
from JumpScale9 import j
# import struct

ServerClass = j.servers.gedis.baseclass_get()

class GedisExampleServer(ServerClass):
    """
        methods found here will be added to the server,
        when calling them with redis client make sure you
        use their name as is, without _cmd in the end

        if it is testtest_cmd, use testtest
        don't capitilize the whole word
    """
    def __init__(self,instance, data={}, parent=None, interactive=False):
        ServerClass.__init__(self, instance=instance, data=data,
                              parent=parent, interactive=interactive)

    def ping2_cmd(self, request):
        return "PONG"

    def testb_cmd(self, request):
        return "testworked"

    def testa_cmd(self, request):
        return "testworked"

    def setf_cmd(self, request):
        k, v = request[1], request[2]
        j.servers.gedisexample.mindb[k] = v
        return k

    def incrf_cmd(self, request):
        k = request[1]
        try:
            j.servers.gedisexample.mindb[k] = int(j.servers.gedisexample.mindb.get(k, 0)) + 1
        except:
            raise ValueError("Value isn't an integer: {}".format(j.servers.gedisexample.mindb[k]))
        return j.servers.gedisexample.mindb[k]

    def getf_cmd(self, request):
        k = request[1]
        return j.servers.gedisexample.mindb.get(k, None)

    def set_cmd(self, request):
        k, v = request[1], request[2]
        zdbconn = j.clients.redis.get(port=8888, set_patch=True)  # default port for 0-db
        res = zdbconn.execute_command("SET", k, v)
        return res

    def get_cmd(self, request):
        k = request[1]
        zdbconn = j.clients.redis.get(port=8888, set_patch=True)  # default port for 0-db
        res = zdbconn.execute_command("GET", k)
        return res

    def error_cmd(self, request):
        raise RuntimeError("error")




