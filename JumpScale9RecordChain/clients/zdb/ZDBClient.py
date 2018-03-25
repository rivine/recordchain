
from js9 import j
from pprint import pprint as print
import os
import copy

TEMPLATE = """
addr = "localhost"
port = "9900"
namespace = ""
adminsecret_ = ""
secret_ = ""
mode = "direct"
id_enable = true
delete = false
"""

JSConfigBase = j.tools.configmanager.base_class_config


class ZDBClient(JSConfigBase):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        """
        is connection to ZDB

        - secret is also the name of the directory where zdb data is for this namespace/secret

        config params:
            secret {str} -- is same as namespace id, is a secret to access the data (default: {None})
            port {[int} -- (default: 9900)
            mode -- user,direct,sequential see https://github.com/rivine/0-db/blob/master/README.md
            id_enabled -- if mode: user or sequential then key_enabled needs to be False, there will be pos_id for each change in the DB
            namespace -- zdb supports namespace
            adminsecret does not have to be set, but when you want to create namespaces it is a must

        """
        self.init(instance=instance, data=data, parent=parent, interactive=interactive)

    def init(self,instance, data={}, parent=None, interactive=False, reset=False):

        JSConfigBase.__init__(self, instance=instance, data=data,
                              parent=parent, template=TEMPLATE, ui=None, interactive=interactive)

        if self.config.data["id_enable"]:
            ipath = j.dirs.VARDIR + "/zdb/index/%s.db"%instance
            j.sal.fs.createDir(j.dirs.VARDIR + "/zdb/index")
            if reset:
                j.sal.fs.remove(ipath)
            self._indexfile = j.data.indexfile.get(name=instance, path=ipath, nrbytes=6)
        else:
            self._indexfile = None

        redis = j.clients.redis.get(ipaddr=self.config.data['addr'],
                                    port=self.config.data['port'],
                                    fromcache=False)

        self.client = self._patch_redis_client(redis)

        if self.config.data["adminsecret_"] is not "" and self.config.data["adminsecret_"] is not None:
            self.client.execute_command("AUTH", self.config.data["adminsecret_"])

        self.id_enable = bool(self.config.data["id_enable"])

        if self.id_enable:
            self.config.data["mode"] == "direct"

        self.key_enable = False
        if self.config.data["mode"] == "user":
            if self.id_enable:
                raise RuntimeError("cannot have id_enable and user mode on db")
            self.key_enable = True
        if self.config.data["mode"] == "direct": 
            self.key_enable = False
        if self.config.data["mode"] == "seq": 
            self.key_enable = False
            if self.id_enable:
                raise RuntimeError("cannot have id_enable and seq mode on db")                

        nsname = self.config.data["namespace"]
        secret = self.config.data["secret_"]

        def namespace_init(nsname, secret):
            # means the namespace does already exists
            if secret is "":
                self.client.execute_command("SELECT", nsname)
            else:
                self.client.execute_command("SELECT", nsname, secret)
            self.namespace = nsname

        if self.namespace_exists(nsname):
            namespace_init(nsname, secret)
            self.logger.debug("namespace:%s exists" % nsname)
        else:
            self.client.execute_command("NSNEW", nsname)
            namespace_init(nsname, secret)
            if secret is not "":
                self.client.execute_command(
                    "NSSET", self.namespace, "password", secret)
                self.client.execute_command(
                    "NSSET", self.namespace, "public", "no")
            self.logger.debug("namespace:%s NEW" % nsname)

        self.logger.debug(self.nsinfo)


    def _patch_redis_client(self, redis):
        # don't auto parse response for set, cause it's not 100% redis compatible
        # 0-db does return a key after in set
        del redis.response_callbacks['SET']
        return redis

    def set(self, data, id=None, key=None, checknew=False):
        """[summary]

        Arguments:
            data {str or binary} -- the payload can be e.g. capnp binary

        Keyword Arguments:
            id {int} -- needs id_enabled to be on true, can be used to find info back based on id (default: {None})
                        if None and id_enabled==True then will autoincrement if not given

            key {[type]} -- string, only usable if key_enable == True

        @PARAM checknew, if True will return (key,new) and new is bool
        """
        if self.key_enable:
            if key is None:
                raise j.exceptions.Input("key cannot be None")
            self.client.execute_command("SET", key, data)
            return key

        elif self.id_enable:
            if id is None:
                id = self._indexfile.count
            if checknew:
                if not j.data.types.bytes.check(data):
                    raise j.exceptions.Input("data needs to be binary when checknew feature")
                dataInDB = self.get(id)
                if data == dataInDB:
                    return (id, False)                

            pos = self.client.execute_command("SET", id, data)
            self._indexfile.set(id, pos)

            if checknew:
                return (id,True)

            return id

        else:
            if id is not None or key is not None:
                raise j.exceptions.Input("id and key need to be None because key and id_enable are False")        
            pos = self.client.execute_command("SET", key, data)
            return pos

    def get(self, key):
        """[summary]

        Arguments:
            key {[type]} - - [description] is id or key
        """
        if self.key_enable:
            return self.client.execute_command("GET", key)
        elif self.id_enable:
            if not j.data.types.int.check(key):
                raise j.exceptions.Input("key needs to be int")
            pos = self._indexfile.get(key)
            if pos == b"":
                raise j.exceptions.Input("could not find data with id:%s in database"%key)
            return self.client.execute_command("GET", pos)
        else:
            return self.client.execute_command("GET", pos)


    def exists(self, key):
        """[summary]

        Arguments:
            key {[type]} - - [description] is id or key
        """
        if self.id_enable:
            if not j.data.types.int.check(key):
                raise j.exceptions.Input("key needs to be int")
            pos = self._indexfile.get(key)
            if pos==b'':
                return False
            return self.client.execute_command("EXISTS", pos)
        else:
            return self.client.execute_command("EXISTS", pos)


    @property
    def nsinfo(self):
        res={}
        for item in self.client.execute_command("NSINFO",self.namespace).decode().split("\n"):
            item=item.strip()
            if item == "":
                continue
            if item[0] == "#":
                continue
            if ":" in item:
                key,val=item.split(":")
                try:
                    val=int(val)
                    res[key] = val
                    continue
                except:
                    pass
                try:
                    val=float(val)
                    res[key] = val
                    continue
                except:
                    pass
                res[key] = str(val).strip()
        return res

    def list(self,start=None,end=None):
        res = self._indexfile.list(start=start,end =end)
        return [i for i in res.keys()]

    def iterate(self, method, start=None, end=None,result=None):
        """walk over the data and apply method as follows

        ONLY works for when id_enable is True

        call for each item:
            '''
            for each:
                result = method(id,data,result)
            '''
        result is the result of the previous call to the method

        Arguments:
            method {python method} -- will be called for each item found in the file

        Keyword Arguments:
            start {int} -- start id (default: {0})
            end {int} -- end id (default: {0}, which means end of file)
        """
        if self.id_enable == False:
            raise RuntimeError("only id_enable supported for iterate")

        if start is not None:
            id = start
        else:
            id=0
            
        self._indexfile._f.seek(self._indexfile._offset(id))

        while True:
            pos = self._indexfile._f.read(self._indexfile.nrbytes)
            if len(pos) < self._indexfile.nrbytes:
                break  # EOF

            data = self.client.execute_command("GET", pos)
            
            result = method(id, data, result=result)
            id += 1
            if end is not None and id > end:
                break

        return result

    def namespace_exists(self,name):
        try:
            self.client.execute_command("NSINFO",name)
            return True
        except Exception as e:
            if not "Namespace not found" in str(e):
                raise RuntimeError("could not check namespace:%s, error:%s"%(name,e))
            return False

    def namespace_new(self,name,secret = "", maxsize = 0, instance=None):
        if self.namespace_exists(name):
            raise RuntimeError("namespace already exists:%s"%name)

        data = copy.copy(self.config.data)
        data["namespace"] = name
        data["secret_"] = secret
        if instance is not None:
            self.instance = instance
        self.init(self.instance, data=data,reset=True)

        if maxsize is not 0:
            self.client.execute_command("NSSET", self.namespace, "maxsize", maxsize)

    @property
    def count(self):
        i = self.nsinfo
        if self.id_enable:
            return self._indexfile.count
        else:
            return i["entries"]

    def test(self):

        nr = self.nsinfo["entries"]
        assert nr == 0
        # do test to see that we can compare
        id = self.set(b"r")
        assert id == 0 #because should be a new DB when testing
        assert  self.get(id) == b"r"
        newid, exists = self.set(b"r",id=id,checknew=True)
        assert exists == False
        assert newid == id

        nr = self.nsinfo["entries"]

        self.set("test",1)
        print (self.nsinfo)

        #test the list function
        assert self.list(0,0) == [0]
        assert self.list(0,1) == [0,1]
        assert self.list(1,1) == [1]

        res=self.list()
        assert res == [0, 1]

        print(res)

        result = {}
        def test(id,data,result):
            print("%s:%s"%(id,data))
            result[id]=data
            return result

        result = self.iterate(test,result={})

        assert self.list(start=newid,end=newid) == [newid]

        result = self.iterate(test,result={},start=newid,end=newid)

        assert result ==  {newid: b'r'}

        assert self.exists(newid)

        def dumpdata():

            if self.key_enable:
                inputs = {}
                for i in range(4):
                    data = os.urandom(4096)
                    key = self.set(data, key=str(i))
                    inputs[key] = data

            elif self.id_enable:
                inputs = {}
                for i in range(4):
                    data = os.urandom(4096)
                    key = self.set(data)
                    inputs[key] = data

            for k, expected in inputs.items():
                actual = self.get(k)
                assert expected == actual

        dumpdata() #is in default namespace

        for i in range(1000):
            nsname = "testns_%s"%i
            exists = self.namespace_exists(nsname)
            if not exists:
                break

        print ("count:%s"%self.count)
        
        self.namespace_new(nsname,secret="1234",maxsize = 1000,instance=None)

        assert self.nsinfo["data_limits_bytes"] == 1000
        assert self.nsinfo["data_size_bytes"] == 0
        assert self.nsinfo["data_size_mb"] == 0.0
        assert self.nsinfo["entries"] == 0
        assert self.nsinfo["index_size_bytes"] == 0
        assert self.nsinfo["index_size_kb"] == 0.0
        assert self.nsinfo["name"] == nsname
        assert self.nsinfo["password"] == "yes"
        assert self.nsinfo["public"] == "no"

        assert self.namespace == nsname

        #both should be same
        id = self.set(b"a")
        assert self.get(id) == b"a"
        assert self._indexfile.count == 1
        assert self.nsinfo["entries"] == 1

        try:
            dumpdata()
        except Exception as e:
            assert "No space left" in str(e)

        self.namespace_new(nsname+"2",secret="1234",instance=None)

        nritems= 100000
        j.tools.timer.start("zdb")
        
        print("perftest for 100.000 records, should get above 10k per sec")
        for i in range(nritems):
            id = self.set(b"a")

        j.tools.timer.stop(nritems)

        