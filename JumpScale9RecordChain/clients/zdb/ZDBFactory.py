
from js9 import j
from pprint import pprint as print

from .ZDBClient import ZDBClient

JSConfigBase = j.tools.configmanager.base_class_configs


class ZDBFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.clients.zdb"
        super(ZDBFactory, self).__init__(ZDBClient)

    def configure(self, instance="main", namespace="default", secret="", addr="localhost", port=None, adminsecret="", mode="user", id_enable=False, started=False):

        if port is None:
            raise InputError("port cannot be None")

        data = {}
        data["addr"] = addr
        data["port"] = int(port)
        data["mode"] = str(mode)
        data["namespace"] = str(namespace)
        data["id_enable"] = bool(id_enable)
        data["adminsecret_"] = adminsecret
        data["secret_"] = secret
        return self.get(instance=instance, data=data, create=True, interactive=False, started=started)

    def test(self):
        """
        js9 'j.data.zdb.test()'

        """
        db = self.configure(port=9900)
        db.test()
