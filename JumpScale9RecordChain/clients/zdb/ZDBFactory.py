
from js9 import j
from pprint import pprint as print

from .ZDBClient import ZDBClient

JSConfigBase = j.tools.configmanager.base_class_configs


class ZDBFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.clients.zdb"
        super(ZDBFactory, self).__init__(ZDBClient)

    def configure(self, instance="main", namespace="default", secret="", addr="localhost", port=None, adminsecret="", mode="user", id_enable=False, started=True):

        if port is None:
            raise InputError("port cannot be None")

        data = {}
        data["addr"] = addr
        data["port"] = str(port)
        data["mode"] = str(mode)
        data["namespace"] = str(namespace)
        # data["id_enable"] = bool(id_enable)
        data["adminsecret_"] = adminsecret
        data["secret_"] = secret
        return self.get(instance=instance, data=data, create=True, interactive=False, started=started)

    def test(self,start=True):
        """
        js9 'j.clients.zdb.test(start=False)'

        """

        db = j.servers.zdb.configure(instance="test", adminsecret="1234", reset=True, mode="seq", id_enable=False)

        if start:    
            db.stop()
            db.start()

        cl = db.client_get()
        cl.test()

        #TODO: *1 need to test the other modes as well