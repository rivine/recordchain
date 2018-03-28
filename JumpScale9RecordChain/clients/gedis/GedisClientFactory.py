
from pprint import pprint as print

from js9 import j


JSBASE = j.application.jsbase_get_class()


class GedisClientFactory(JSBASE):
    """
    is nothing more for now than the redis_config client
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.gedis"
        JSBASE.__init__(self)

    def configure(self, instance="core",ipaddr="localhost", \
            port=6379, password="", unixsocket="", 
            ssl=False, ssl_keyfile=None, ssl_certfile=None):


        return j.clients.redis_config.configure(instance=instance,
            ipaddr=ipaddr ,port=port ,password=password, unixsocket=unixsocket,
            set_patch=True, ssl=ssl, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile).redis

            
        