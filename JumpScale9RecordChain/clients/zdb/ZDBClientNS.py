
from js9 import j
from pprint import pprint as print
import os
import struct
import copy
import redis

JSBASE = j.application.jsbase_get_class()


class ZDBClientNS(JSBASE):

    def __init__(self, zdbclient, nsname):
        """
        is connection to ZDB

        - secret is also the name of the directory where zdb data is for this namespace/secret

        config params:
            secret {str} -- is same as namespace id, is a secret to access the data (default: {None})
            port {[int} -- (default: 9900)
            mode -- user,direct,seq(uential) see https://github.com/rivine/0-db/blob/master/README.md
            namespace -- zdb supports namespace
            adminsecret does not have to be set, but when you want to create namespaces it is a must

        """
        JSBASE.__init__(self)
        self.zdbclient = zdbclient
        self.redis = j.clients.redis.get(ipaddr=zdbclient.config.data['addr'],
                                         port=zdbclient.config.data['port'],
                                         fromcache=False)

        self.redis = self._patch_redis_client(self.redis)

        self.nsname = nsname.lower().strip()
        self.mode = self.zdbclient.mode

        if self.adminsecret is not "":
            self.redis.execute_command("AUTH", self.adminsecret)

        # put secret on namespace & select namespace
        if self.secret is "":
            self.redis.execute_command("SELECT", self.nsname)
        else:
            self.redis.execute_command("SELECT", self.nsname, self.secret)

    @property
    def adminsecret(self):
        return self.zdbclient.adminsecret

    @property
    def secret(self):
        if self.nsname in self.zdbclient.secrets.keys():
            return self.zdbclient.secrets[self.nsname]
        else:
            return self.zdbclient.secrets["default"]

    def _patch_redis_client(self, redis):
        # don't auto parse response for set, cause it's not 100% redis compatible
        # 0-db does return a key after in set
        del redis.response_callbacks['SET']
        return redis

    def _key_get(self, key, set=True):

        if self.mode == "seq":
            if key is None:
                key = ""
            else:
                key = struct.pack("<I", key)
        elif self.mode == "direct":
            if set:
                if not key in ["", None]:
                    raise j.exceptions.Input("key need to be None or empty string")
                if key is None:
                    key = ""
            else:
                if key in ["", None]:
                    raise j.exceptions.Input("key cannot be None or empty string")
        elif self.mode == "user":
            if key in ["", None]:
                raise j.exceptions.Input("key cannot be None or empty string")
        return key

    def set(self, data, key=None, check_new=False):
        """[summary]

        Arguments:
            data {str or binary} -- the payload can be e.g. capnp binary

        Keyword Arguments:
            key {int} -- when used in sequential mode
                        can be None or int
                        when None it means its a new object, so will be appended

            key {[type]} -- string, only usable for user mode


        """
        k = self._key_get(key, set=True)

        try:
            res = self.redis.execute_command("SET", k, data)
        except Exception as e:
            raise j.exceptions.Input(e)

        new = True
        if res:
            key = struct.unpack("<I", res)[0]
        if not res: 
            new = False
            self.logger.info("Value for key {} is the same. Ignoring".format(key))
        if check_new:
            return key, new
        return key

    def get(self, key):
        """[summary]

        Keyword Arguments:
            key {int} -- when used in sequential mode
                        can be None or int
                        when None it means its a new object, so will be appended

            key {[type]} -- string, only usable for user mode

            key {[6 byte binary]} -- is binary position is for direct mode

        """
        key = self._key_get(key, set=False)
        return self.redis.execute_command("GET", key)

    def exists(self, key):
        """[summary]

        Arguments:
            key {[type]} - - [description] is id or key
        """
        key = self._key_get(key, set=False)

        return self.redis.execute_command("EXISTS", key) == 1

        # if self.mode=="seq":
        #     id = struct.pack("<I", key)
        #     return self.redis.execute_command("GET", id) is not None
        # elif self.id_enable:
        #     if not j.data.types.int.check(key):
        #         raise j.exceptions.Input("key needs to be int")
        #     pos = self._indexfile.get(key)
        #     if pos == b'':
        #         return False
        #     return self.redis.execute_command("EXISTS", pos)
        # else:
        #     return self.redis.execute_command("EXISTS", pos)

    @property
    def nsinfo(self):
        res = {}
        for item in self.redis.execute_command("NSINFO", self.nsname).decode().split("\n"):
            item = item.strip()
            if item == "":
                continue
            if item[0] == "#":
                continue
            if ":" in item:
                key, val = item.split(":")
                try:
                    val = int(val)
                    res[key] = val
                    continue
                except:
                    pass
                try:
                    val = float(val)
                    res[key] = val
                    continue
                except:
                    pass
                res[key] = str(val).strip()
        return res

    def list(self, key_start=None, key_end=None, direction="forward", nr_records=100000, result=None):
        if result is None:
            result = []

        def do(arg, result):
            result.append(arg)
            return result

        self.iterate(do, key_start=key_start, key_end=key_end, direction=direction, nr_records=nr_records, _keyonly=True, result=result)
        return result

    def iterate(self, method, key_start=None, key_end=None, direction="forward", nr_records=100000, _keyonly=False, result=None):
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
            key_start is the start key, if not given will be start of database when direction = forward, else end
            key_end is the end key, if not given will be end of database when direction = forward, else start

        """
        if result is None:
            result = []

        if self.mode == "seq":
            key_start = key_start - 1 if key_start else None
            key_end = key_end - 1 if key_end else key_end

        keyb = self._key_get(key_start, set=False)
        keye = self._key_get(key_end, set=False)

        if direction == "forward":
            CMD = "SCANX" # SCAN but to avoid redis lib conventions
        else:
            CMD = "RSCAN"

        nr = 0
        while nr < nr_records:
            try:
                if keyb in [None, ""]:
                    keyb_new = self.redis.execute_command(CMD)[0]
                else:
                    keyb_new = self.redis.execute_command(CMD, keyb)[0]
            except redis.ResponseError as e:
                if e.args[0] == 'No more data':
                    return result

            if self.mode == "seq":
                key_new = struct.unpack("<I", keyb_new)[0]
            else:
                key_new = keyb_new

            if _keyonly:
                result = method(key_new, result)
            else:
                data = self.redis.execute_command("GET", keyb_new)
                result = method(key_new, data, result)

            keyb = keyb_new
            if keyb == keye:
                break
            nr += 1

        return result

    @property
    def count(self):
        i = self.nsinfo
        return i["entries"]

    def test(self):

        nr = self.nsinfo["entries"]
        assert nr == 0
        # do test to see that we can compare
        id = self.set(b"r")
        assert id == 0
        assert self.get(id) == b"r"

        id2 = self.set(b"b")
        assert id2 == 1


        # Test that updating key with its current value doesn't change key
        newid, exists = self.set(b"r", key=id, check_new=True)
        assert exists is False
        assert newid == id

        nr = self.nsinfo["entries"]
        assert nr == 2

        # self.set("test", 1)
        # print (self.nsinfo)

        # test the list function
        assert self.list() == [0, 1]
        assert self.list(1) == [1]
        assert self.list(0) == [0, 1]

        result = {}

        def test(id, data, result):
            print("%s:%s" % (id, data))
            result[id] = data
            return result

        result = self.iterate(test, result={})

        assert self.list(key_start=newid, key_end=newid) == [newid]

        result = self.iterate(test, result={}, key_start=newid, key_end=newid)

        assert result == {newid: b'r'}

        assert self.exists(newid)

        def dumpdata():
            inputs = {}
            for i in range(4):
                data = os.urandom(4096)
                key = self.set(data)
                inputs[key] = data

            inputs = {}
            for k, expected in inputs.items():
                actual = self.get(k)
                assert expected == actual

        dumpdata()  # is in default namespace

        for i in range(1000):
            nsname = "testns_%s" % i
            exists = self.nsinfo['name'] == nsname
            if not exists:
                break

        print ("count:%s" % self.count)

        namespace = self.zdbclient.namespace_new(nsname, secret="1234", maxsize=1000)

        assert namespace.nsinfo["data_limits_bytes"] == 1000
        assert namespace.nsinfo["data_size_bytes"] == 0
        assert namespace.nsinfo["data_size_mb"] == 0.0
        assert namespace.nsinfo["entries"] == 0
        assert namespace.nsinfo["index_size_bytes"] == 0
        assert namespace.nsinfo["index_size_kb"] == 0.0
        assert namespace.nsinfo["name"] == nsname
        assert namespace.nsinfo["password"] == "yes"
        assert namespace.nsinfo["public"] == "no"


        id = namespace.set(b"a")
        assert namespace.get(id) == b"a"
        assert namespace.count == 1
        assert namespace.nsinfo["entries"] == 1

        try:
            dumpdata()
        except Exception as e:
            assert "No space left" in str(e)

        namespace2 = self.zdbclient.namespace_new(nsname+"2", secret="1234")

        nritems = 100000
        j.tools.timer.start("zdb")

        print("perftest for 100.000 records, should get above 10k per sec")
        for i in range(nritems):
            id = namespace2.set(b"a")

        j.tools.timer.stop(nritems)
