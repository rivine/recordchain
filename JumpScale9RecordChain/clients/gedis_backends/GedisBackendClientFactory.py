from js9 import j
from .GunClient import GunClient

JSConfigBase = j.tools.configmanager.base_class_configs

ALLOWED_TYPES = {
    'gun': GunClient
} # available clients, add to this if a new client is added

class GedisBackendClientFactory(JSConfigBase):

    def __init__(self):        
        self.__jslocation__ = "j.clients.gedis_backend"
        JSConfigBase.__init__(self, GunClient)

    def get(self, instance="main", data={}, create=True, die=True, interactive=True, type='gun'):
        if not create and instance not in self.list():
            if die:
                raise RuntimeError("could not find instance:%s" % (instance))
            else:
                return None
        if type not in ALLOWED_TYPES:
            raise RuntimeError("Specified type not allowed")
        return ALLOWED_TYPES[type](instance=instance, data=data, interactive=interactive, parent=self)



