
from js9 import j
from pprint import pprint as print

from .BCDB import BCDB


JSConfigBase = j.tools.configmanager.base_class_configs


class BCDBFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.data.bcdb"
        super().__init__(child_class=BCDB)

    def db_start(self, instance, adminsecret, port=8888, reset=False):
        self.instance_last = instance
        s = j.servers.zdb.configure(instance=instance, port=port, mode="direct", reset=reset, adminsecret=adminsecret, start=True, id_enable=True)

    def get(self, instance):
        s = j.servers.zdb.get(instance=instance)
        data = {}
        data["zdb_adminsecret_"] = s.config.data["adminsecret_"]
        data["zdb_port"] = s.config.data["port"]
        bcdb = self._child_class(instance=instance, data=data, parent=self, interactive=False)
        bcdb.server = s
        return bcdb

    def test(self):
        """
        js9 'j.data.bcdb.test()'
        """

        schema = """
        @url = despiegk.test
        @name = TestObj
        llist2 = "" (LS)    
        name* = ""    
        email* = ""
        nr = 0
        date_start = 0 (D)
        description = ""
        token_price = "10 USD" (N)
        cost_estimate:hw_cost = 0.0 #this is a comment
        llist = []
        llist3 = "1,2,3" (LF)
        llist4 = "1,2,3" (L)
        llist5 = "1,2,3" (LI)
        U = 0.0
        #pool_type = "managed,unmanaged" (E)  #NOT DONE FOR NOW
        """

        schema2 = """
        @url = despiegk.test
        @name = TestObj2
        name* = ""    
        email* = ""
        nr = 0
        """

        def load():
            self.db_start("test", adminsecret="g007g", reset=True)
            db = self.get("test")
            t = db.table_get(name="t1", schema=schema)   #why does name have to be t1
            t2 = db.table_get(name="t1", schema=schema2)

            for i in range(10):
                o = t.new()
                o.llist.append(1)
                o.llist2.append("yes")
                o.llist2.append("no")
                o.llist3.append(1.2)
                o.U = 1.1
                o.nr = 1
                o.token_price = "10 EUR"
                o.description = "something"
                o.name = "name%s" % i
                o.email = "info%s@something.com" % i
                o2 = t.set(o)
                assert o2.id == i

            o3 = t.get(o2.id)
            assert o3.id == o2.id

            assert o3.ddict == o2.ddict
            assert o3.ddict == o.ddict

        load()

        db = self.get("test")
        t = db.table_get(name="t1", schema=schema)

        res = t.find(name="name1", email="info2@something.com")
        assert len(res) == 0

        res = t.find(name="name2")
        assert len(res) == 1
        assert res[0].name == "name2"

        res = t.find(name="name2", email="info2@something.com")
        assert len(res) == 1
        assert res[0].name == "name2"

        o = res[0]
        
        o.name = "name2"
        assert o.changed_prop == False  # because data did not change, was already that data
        o.name = "name3"
        assert o.changed_prop == True  # now it really changed

        assert o.ddict["name"] == "name3"
