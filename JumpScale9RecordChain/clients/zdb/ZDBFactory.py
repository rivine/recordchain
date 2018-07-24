
from js9 import j
from pprint import pprint as print

from .ZDBClient import ZDBClient

JSConfigBase = j.tools.configmanager.base_class_configs


class ZDBFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.clients.zdb"
        super(ZDBFactory, self).__init__(ZDBClient)

    def configure(self, instance="main", secrets="", addr="localhost", port=None, adminsecret="", mode="user",encryptionkey=""):

        if port is None:
            raise InputError("port cannot be None")

        data = {}
        data["addr"] = addr
        data["port"] = str(port)
        data["mode"] = str(mode)
        data["adminsecret_"] = adminsecret
        data["secrets_"] = secrets
        data["encryptionkey_"] = encryptionkey
        return self.get(instance=instance, data=data, create=True, interactive=False)

    def test(self,start=True):
        """
        js9 'j.clients.zdb.test(start=False)'

        """

        #will delete the config info
        self.delete(instance="test")

        db = j.servers.zdb.configure(instance="test", adminsecret="123456", reset=True, mode="seq")

        if start:    
            db.stop()
            db.start()

        cl = db.client_get(secrets="1234",encryptionkey="abcdefgh")
        cl1 = cl.namespace_new("test")
        cl1.test()


        #TODO: *1 need to test the other modes as well