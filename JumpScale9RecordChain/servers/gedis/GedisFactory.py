
from pprint import pprint as print

from js9 import j

from .server import RedisServer

JSBASE = j.application.jsbase_get_class()


class GedisFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.servers.gedis"
        JSBASE.__init__(self)

    def get_base_class(self):
        return RedisServer
