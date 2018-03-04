
from js9 import j
from pprint import pprint as print
import os

TEMPLATE = """
addr = "localhost"
port = "9900"
secret_ = ""
path = ""
key_enable = false
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
            key_enable -- if used then ZDB will put key metadata in memory to find position back in the DB files
            id_enabled -- if used then key_enabled needs to be False, there will be pos_id for each change in the DB

        pos_id = unique id which is the position of the last inserted data in the DB
        id = incremental id per type of data object
        """

        JSConfigBase.__init__(self, instance=instance, data=data,
                              parent=parent, template=TEMPLATE, ui=None, interactive=interactive)

        # re-enable once 0-db support creating namespace and protect it with password
        # if not self.config.data["secret_"]:
        #     raise RuntimeError("cannot have empty secret")

        if self.config.data["key_enable"] and self.config.data["id_enabled"]:
            raise RuntimeError("have to choose or using id or using id")

        if self.config.data["id_enable"]:
            ipath = self.config.data["path"] + "/indexfile.db"
            self._indexfile = j.data.indexfile.get(name=instance, path=ipath, nrbytes=6)
        else:
            self._indexfile = None

        redis = j.clients.redis.get(ipaddr=self.config.data['addr'],
                                    port=self.config.data['port'],
                                    password=self.config.data['secret_'],
                                    fromcache=False)
        self._redis = self._patch_redis_client(redis)

    def _patch_redis_client(self, redis):
        # don't auto parse response for set, cause it's not 100% redis compatible
        # 0-db does return a key after in set
        del redis.response_callbacks['SET']
        return redis

    def set(self, data, id=None, key=None):
        """[summary]

        Arguments:
            data {str or binary} -- the payload can be e.g. capnp binary

        Keyword Arguments:
            id {int} -- needs id_enabled to be on true, can be used to find info back based on id (default: {None})
                        if None and id_enabled==True then will autoincrement if not given

            key {[type]} -- string, only usable if key_enable == True
        """
        if self.config.data['key_enable']:
            if key is None:
                raise j.exceptions.Input("key cannot be None")
            key = self._redis.execute_command("SET", key, data)
            return key

        elif self.config.data['id_enable']:
            if id is None:
                id = self._indexfile.count
            else:
                raise NotImplementedError()

            key = self._redis.execute_command("SET", '', data)
            self._indexfile.set(id, key)
            return id
        else:
            raise j.exceptions.RuntimeError("unsupported mode")

    def get(self, key):
        """[summary]

        Arguments:
            key {[type]} - - [description]
        """
        if self.config.data['key_enable']:
            data = self._redis.execute_command("GET", key)
        elif self.config.data['id_enable']:
            zdb_key = self._indexfile.get(key)
            data = self._redis.execute_command("GET", zdb_key)
        else:
            raise j.exceptions.RuntimeError("unsupported mode")
        return data

    def test(self):
        if self.config.data['key_enable']:
            inputs = {}
            for i in range(10):
                data = os.urandom(4096)
                key = self.set(data, key=str(i))
                inputs[key] = data

        elif self.config.data['id_enable']:
            inputs = {}
            for i in range(10):
                data = os.urandom(4096)
                key = self.set(data)
                inputs[key] = data

        for k, expected in inputs.items():
            actual = self.get(k)
            assert expected == actual
