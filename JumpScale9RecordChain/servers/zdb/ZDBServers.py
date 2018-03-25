
from js9 import j
from pprint import pprint as print

from .ZDBServer import ZDBServer

JSConfigBase = j.tools.configmanager.base_class_configs


class ZDBServers(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.servers.zdb"
        super().__init__(child_class=ZDBServer)
        self.rootdir = j.sal.fs.joinPaths(j.dirs.VARDIR, 'zdb')

    def configure(self, instance="main", adminsecret="", mode = "user", rootdir=None, addr="127.0.0.1", port=9900, verbose = True, id_enable=True, reset=False):
        """
        read more info at https://github.com/rivine/0-db/blob/master/README.md
        mode: user,direct,seq

        id_enable means we have an index file where we keep relation between id & position in the database (zdb), based on int

        js9 'j.servers.zdb.configure(instance="main",port=8888,reset=True)'

        """

        if mode not in ["user","seq","direct"]:
            raise RuntimeError("only supported modes are: user,seq,direct, got:%s"%mode)            

        if not rootdir:
            rootdir = self.rootdir

        path = j.sal.fs.joinPaths(rootdir, instance)

        data = {}
        data["path"] = path
        data["addr"] = addr
        data["port"] = int(port)
        data["mode"] = mode
        data["adminsecret_"] = adminsecret
        data["verbose"] = verbose
        data["id_enable"] = id_enable

        s = self.get(instance=instance, data=data)
        if reset:
            s.destroy()

        return s

    def start(self,instance="main"):
        """
        js9 'j.servers.zdb.start(instance="main")'
        """
        s= self.get(instance=instance)
        s.start()

    def build(self):
        """
        js9 'j.servers.zdb.build()'
        """
        j.tools.prefab.local.zero_os.zos_db.build(install=True)

    def test(self):
        """
        js9 'j.servers.zdb.test()'
        """
        # self.build()
        db = self.get_by_params(instance="test",adminsecret="1234",reset=True)
        db.start()
        cl = db.client_get()
        cl.test()
