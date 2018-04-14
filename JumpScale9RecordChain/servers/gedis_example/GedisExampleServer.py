
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

    def ping2(self):

        return "PONG"

    def testb(self):
        """
        test with empty schema arguments
        ```
        ```
        test with empty schema arguments
        """        
        return "testworked"

    def testa(self):
        """
        ```
        ```
        """        
        return "testworked"

    def setf(self, key,val):
        """
        ```
        key = "" (S)
        val = ""
        ```
        """          
        j.servers.gedisexample.mindb[key] = val
        return key

    def incrf(self, key):
        """
        ```
        #increment happens per key
        key = "" (S) 
        ```
        """            
        k = key
        try:
            j.servers.gedisexample.mindb[k] = int(j.servers.gedisexample.mindb.get(k, 0)) + 1
        except:
            raise ValueError("Value isn't an integer: {}".format(j.servers.gedisexample.mindb[k]))
        return j.servers.gedisexample.mindb[k]

    def getf_cmd(self, k):
        """
        ```
        key = "" (S) 
        ```
        """   
        return j.servers.gedisexample.mindb.get(k, None)

    def set(self, k,v):
        """
        ```
        key = "" (S)
        val = ""
        ```
        """          
        zdbconn = j.clients.redis.get(port=8888, set_patch=True)  # default port for 0-db
        res = zdbconn.execute_command("SET", k, v)
        return res

    def get_cmd(self, k):
        """
        ```        
        k = "" (S)  #key to fetch
        ```
        """   
        zdbconn = j.clients.redis.get(port=8888, set_patch=True)  # default port for 0-db
        res = zdbconn.execute_command("GET", k)
        return res

    def error_cmd(self):
        raise RuntimeError("error")




