
from js9 import j
from pprint import pprint as print

from .ZDBClient import ZDBClient

JSConfigBase = j.tools.configmanager.base_class_configs


class ZDBFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.data.zdb"
        super(ZDBFactory, self).__init__(ZDBClient)

    def get_by_params(self, instance="main", secret=None, path=None, addr=None, port=None):

        if not secret or not path or not addr or not port:
            server = j.servers.zdb.get(instance)

        if path is None:
            path = server.config.data["path"]

        if addr is None:
            addr = server.config.data["addr"]

        if port is None:
            port = server.config.data["port"]

        # this doesn't exsits on j.servers.zdb
        # if secret is None:
        #     secret = server.config.data["secret"]

        data = {}
        data["addr"] = addr
        data["port"] = int(port)
        if secret is not None:
            data["secret_"] = secret
        data["path"] = path
        return self.get(instance=instance, data=data, create=True)

    def test(self):
        """
        js9 'j.data.zdb.test()'

        """
        db = self.get()
        db.test()
