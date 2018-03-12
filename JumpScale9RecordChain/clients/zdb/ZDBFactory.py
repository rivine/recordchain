
from js9 import j
from pprint import pprint as print

from .ZDBClient import ZDBClient

JSConfigBase = j.tools.configmanager.base_class_configs


class ZDBFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.clients.zdb"
        super(ZDBFactory, self).__init__(ZDBClient)

    def get_by_params(self, instance="main", namespace="default", secret="", addr=None, port=None, adminsecret="", mode="direct", id_enable=True):

        if not secret or not path or not addr or not port:
            server = j.servers.zdb.get(instance)

        if addr is None:
            addr = server.config.data["addr"]

        if port is None:
            port = server.config.data["port"]
        

        # this doesn't exists on j.servers.zdb
        # if secret is None:
        #     secret = server.config.data["secret"]

        data = {}
        data["addr"] = addr
        data["port"] = int(port)
        data["mode"] = str(mode)
        data["namespace"] = str(namespace)
        data["id_enable"] = bool(id_enable)
        data["adminsecret_"] = adminsecret    
        data["secret_"] = secret
        return self.get(instance=instance, data=data, create=True)

    def test(self):
        """
        js9 'j.data.zdb.test()'

        """
        db = self.get()
        db.test()
