
from js9 import j
from pprint import pprint as print

from .ZDBServer import ZDBServer

JSConfigBase = j.tools.configmanager.base_class_configs


class ZDBServers(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.servers.zdb"
        super().__init__(child_class=ZDBServer)
        self.rootdir = j.sal.fs.joinPaths(j.dirs.VARDIR, 'zdb')

    def configure(self, instance="main", adminsecret="", mode="user", rootdir=None, addr="127.0.0.1", port=9900, verbose=True, reset=False, start=False):
        """
        read more info at https://github.com/rivine/0-db/blob/master/README.md
        mode: user,direct,seq

        js9 'j.servers.zdb.configure(instance="main",port=8888,reset=True)'

        """

        if mode not in ["user", "seq", "direct"]:
            raise RuntimeError("only supported modes are: user,seq,direct, got:%s" % mode)

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

        instance = self.get(instance=instance, data=data,interactive=False)
        if reset:
            instance.destroy()

        if start:
            instance.start()

        return instance

    def start(self, instance="main"):
        """
        js9 'j.servers.zdb.start(instance="main")'
        """
        s = self.get(instance=instance)
        s.start()

    def build(self):
        """
        js9 'j.servers.zdb.build()'
        """
        j.tools.prefab.local.zero_os.zos_db.build(install=True,reset=True)

    def test(self,build=False):
        """
        js9 'j.servers.zdb.test(build=True)'
        """
        if build:
            self.build()
        db = self.configure(instance="test", adminsecret="1234", reset=True, mode="direct")
        db.stop()
        db.start()
        cl = db.client_get()
        cl.test()

    def test_seq(self):
        """
        js9 'j.servers.zdb.test_seq()'
        """
        # self.build()
        db = self.configure(instance="test", adminsecret="1234", reset=True, mode="seq")
        db.stop()
        db.start()
        db = self.get("test")
        cl = db.client_get()
        nr = cl.nsinfo["entries"]
        assert nr == 0

        for i in range(10):
            id=cl.set("test")
            assert cl.get(id)==b"test"

        nr = cl.nsinfo["entries"]
        assert nr == 10
            
        cl.set("test2",2)
        assert cl.get(2)==b"test2"

        def m(id,data,result):
            print("%s:%s"%(id,data))

        cl.iterate(m)
            