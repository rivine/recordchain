import os
import sys
from js9 import j
import imp
from redis.connection import ConnectionError


TEMPLATE = """
host = "127.0.0.1"
port = "9900"
adminsecret_ = ""
ssl = false
sslkey = ""
"""

JSConfigBase = j.tools.configmanager.base_class_config


class Models():
    def __init__(self):
        pass


class CmdsBase():
    def __init__(self):
        pass


class GedisClient(JSConfigBase):

    def __init__(self, instance, data={}, parent=None, interactive=False, reset=False):
        JSConfigBase.__init__(self, instance=instance, data=data, parent=parent,template=TEMPLATE , interactive=interactive)

        j.clients.gedis2.latest = self

        self.code_generated_dir = j.sal.fs.joinPaths(j.dirs.VARDIR, "codegen", "gedis2", instance, "client")
        j.sal.fs.createDir(self.code_generated_dir)
        j.sal.fs.touch(j.sal.fs.joinPaths(self.code_generated_dir, '__init__.py'))

        if self.code_generated_dir not in sys.path:
            sys.path.append(self.code_generated_dir)

        self._redis = None

        self.models = Models()
        self.cmds = CmdsBase()
        self.cmds_meta = {}
        self._connected = True

        test = self.redis.execute_command("system.ping")

        if test != b'PONG':
            raise RuntimeError('Can not ping server')
        # this will make sure we have all the local schemas
        schemas_meta = self.redis.execute_command("system.core_schemas_get")
        schemas_meta = j.data.serializer.msgpack.loads(schemas_meta)
        for key,txt in schemas_meta.items():
            if key not in j.data.schema.schemas:
                j.data.schema.schema_from_text(txt,url=key)

        schema_urls = self.redis.execute_command("system.schema_urls")
        self.schema_urls = j.data.serializer.msgpack.loads(schema_urls)

        try:
            # LOW LEVEL AT THIS TIME BUT TO SHOW SOMETHING
            cmds_meta =self.redis.execute_command("system.api_meta")
            cmds_meta = j.data.serializer.msgpack.loads(cmds_meta)
            self.namespace = cmds_meta["namespace"]
            for namespace_full, capnpbin in cmds_meta["cmds"].items():
                shortname = namespace_full.split(".")[-1]
                if not shortname.startswith("model"):
                    self.cmds_meta[namespace_full] = j.servers.gedis2.cmds_get(
                        namespace_full,
                        capnpbin
                    ).cmds
        except ConnectionError:
            self.logger.error('Connection error')
            self._connected  = False
            return

        self.generate(reset=reset)

    def generate(self, reset=False):
        for schema_url in self.schema_urls:

            fname = "model_%s" % schema_url.replace(".","_")
            dest = os.path.join(self.code_generated_dir, "%s.py"%fname)

            if reset or not j.sal.fs.exists(dest):
                schema = j.data.schema.schema_from_url(schema_url)
                code = j.clients.gedis2.code_model_template.render(obj= schema)
                j.sal.fs.writeFile(dest,code)

            m=imp.load_source(name=fname, pathname=dest)
            self.logger.debug("schema:%s"%fname)
            self.models.__dict__[schema_url.replace(".","_")] = m.model(client=self)

        for nsfull, cmds_ in self.cmds_meta.items():
            cmds = CmdsBase()
            cmds.cmds = cmds_
            cmds.name = nsfull.replace(".","_")
            # for name,cmd in cmds.items():
            location = nsfull.replace(".","_")
            cmds_name_lower = nsfull.split(".")[-1].strip().lower()
            cmds.cmds_name_lower = cmds_name_lower
            fname="cmds_%s"%location
            dest = os.path.join(self.code_generated_dir, "%s.py"%fname)

            if reset or not j.sal.fs.exists(dest):
                code = j.clients.gedis2.code_client_template.render(obj= cmds)
                j.sal.fs.writeFile(dest,code)

            m=imp.load_source(name=fname, pathname=dest)
            self.logger.debug("cmds:%s"%fname)
            self.cmds.__dict__[cmds_name_lower] =m.CMDS(client=self,cmds=cmds.cmds)

    @property
    def redis(self):
        """
        this gets you a redis instance, when executing commands you have to send the name of the function without
        the postfix _cmd as is, do not capitlize it
        if it is testtest_cmd, then you should call it by testtest

        :return: redis instance
        """
        if self._redis is None:
            d = self.config.data
            addr = d["host"]
            port = d["port"]
            secret = d["adminsecret_"]
            ssl_certfile = d['sslkey']

            if d['ssl']:
                if not self.config.data['sslkey']:
                    ssl_certfile = j.sal.fs.joinPaths(os.path.dirname(self.code_generated_dir), 'ca.crt')
                self.logger.info("redisclient: %s:%s (ssl:True  cert:%s)"%(addr, port, ssl_certfile))
            else:
                self.logger.info("redisclient: %s:%s " % (addr, port))

            self._redis = j.clients.redis.get(
                ipaddr=addr,
                port=port,
                password=secret,
                ssl=d["ssl"],
                ssl_ca_certs=ssl_certfile
            )
        return self._redis
