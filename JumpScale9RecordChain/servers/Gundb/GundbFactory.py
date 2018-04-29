
from js9 import j
from .GundbServer import GundbServer

JSConfigBase = j.tools.configmanager.base_class_configs

class GundbFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.servers.gundb"
        JSConfigBase.__init__(self, GundbServer)