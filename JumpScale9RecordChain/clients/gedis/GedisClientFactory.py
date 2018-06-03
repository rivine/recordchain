
from pprint import pprint as print

from js9 import j



JSConfigBase = j.tools.configmanager.base_class_configs
from .GedisClient import GedisClient


class GedisClientFactory(JSConfigBase):
    """
    is nothing more for now than the redis_config client
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.gedis_DONTUSE"
        JSConfigBase.__init__(self, GedisClient)

    def configure(self, instance="core",ipaddr="localhost", \
            port=6379, password="", unixsocket="", 
            ssl=False, ssl_keyfile=None, ssl_certfile=None):

        """
        #TODO:*1 need to define well what this keyfile/certfile is
        """
        data = {}
        data["addr"] = ipaddr
        data["port"] = port
        data["password_"] = password
        data["unixsocket"] = unixsocket
        data["ssl"] = ssl
        if ssl_certfile:
            #check if its a path, if yes load
            data["ssl"] = True 
            data["sslkey"] = True #means path will be used for sslkey at redis client
            
        r = self.get(instance=instance, data=data)

        if ssl_certfile:
            #check if its a path, if yes safe the key paths into config
            r.ssl_keys_save(ssl_certfile)

        return r



            
        