
from js9 import j
from pprint import pprint as print

from .ZDBServer import ZDBServer

JSConfigBase = j.tools.configmanager.base_class_configs


class ZDBServers(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.servers.zdb"
        super().__init__(child_class=ZDBServer)
        self.rootdir = j.sal.fs.joinPaths(j.dirs.VARDIR, 'zdb')

    def get_by_params(self, instance="main", rootdir=None, addr="127.0.0.1", port=9900):

        if not rootdir:
            rootdir = self.rootdir

        path = j.sal.fs.joinPaths(rootdir, instance)

        data = {}
        data["path"] = path
        data["addr"] = addr
        data["port"] = int(port)

        return self.get(instance=instance, data=data)

    def build(self):
        j.tools.prefab.local.zero_os.zos_db.build(install=True)

    def test(self):
        """
        js9 'servers.zdb.test()'
        """
        self.build()
        db = self.get_by_params()
        db.start()
        cl = db.client
        cl.test()
