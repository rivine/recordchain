from js9 import j
import imp

TEMPLATE = """
addr = "127.0.0.1"
port = 6379
password_ = ""
unixsocket = ""
ssl = false
sslkey = false
"""

JSConfigBase = j.tools.configmanager.base_class_config

#WILL HAVE METHODS IN FUTURE TO GENERATE CLIENT METHODS AUTOMATICALLY

class Models():
    def __init__(self):
        pass

class CmdsBase():
    def __init__(self):
        pass


class GedisClient(JSConfigBase):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigBase.__init__(self, instance=instance, data=data,
                              parent=parent, template=TEMPLATE, interactive=interactive)
        self._redis = None

        self.models = Models()
        self.cmds = CmdsBase()

        #LOW LEVEL AT THIS TIME BUT TO SHOW SOMETHING
        cmds_meta =self.redis.execute_command("system.api_meta")
        cmds_meta = j.data.serializer.msgpack.loads(cmds_meta)
        self.cmds_meta = {}
        self.namespace = cmds_meta["namespace"]
        for namespace_full,capnpbin in cmds_meta["cmds"].items():
            shortname = namespace_full.split(".")[-1]
            if not shortname.startswith("model"):
                self.cmds_meta[namespace_full] = j.servers.gedis2.cmds_get(namespace_full,capnpbin).cmds

        #this will make sure we have all the local schemas
        schemas_meta =self.redis.execute_command("system.core_schemas_get")
        schemas_meta = j.data.serializer.msgpack.loads(schemas_meta)
        for key,txt in schemas_meta.items():
            if key not in j.data.schema.schemas:
                j.data.schema.schema_from_text(txt,url=key)


        schema_urls =self.redis.execute_command("system.schema_urls")
        self.schema_urls = j.data.serializer.msgpack.loads(schema_urls)
                
        self.generate()

    def generate(self,reset=True):

        for schema_url in self.schema_urls:
            fname="model_%s"%schema_url.replace(".","_")
            dest = j.clients.gedis2.code_generation_dir+"/%s.py"%fname
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
            dest = j.clients.gedis2.code_generation_dir+"/%s.py"%fname
            # schema = j.data.schema.schema_from_url(schema_url)
            code = j.clients.gedis2.code_client_template.render(obj= cmds)
            j.sal.fs.writeFile(dest,code)
            m=imp.load_source(name=fname, pathname=dest)
            self.logger.debug("cmds:%s"%fname)
            self.cmds.__dict__[cmds_name_lower] =m.CMDS(client=self,cmds=cmds.cmds)

    @property
    def ssl_certfile_path(self):
        p = j.sal.fs.getDirName(self.config.path) + "cert.pem"
        if self.config.data["sslkey"]:
            return p

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
            addr = d["addr"]
            port = d["port"]
            password = d["password_"]
            unixsocket = d["unixsocket"]
            set_patch=True
            ardb_patch=False

            self.logger.info("redisclient: %s:%s (ssl:%s)"%(addr,port,d["ssl"]))

            # NO PATHS IN CONFIG !!!!!!!, needs to come from properties above (convention over configuration)

            ssl_certfile = self.ssl_certfile_path if d['ssl'] else None

            if unixsocket == "":
                unixsocket = None

            # import ipdb; ipdb.set_trace()
            self._redis = j.clients.redis.get(
                ipaddr=addr, port=port, password=password, ssl=d["ssl"], ssl_ca_certs=ssl_certfile)

        return self._redis

    def ssl_keys_save(self,  ssl_certfile):
        if j.sal.fs.exists(ssl_certfile):
            ssl_certfile = j.sal.fs.readFile(ssl_certfile)
        j.sal.fs.writeFile(self.ssl_certfile_path, ssl_certfile)

    def __str__(self):
        return "gedisclient:%-14s %-25s:%-4s (ssl:%s)" % (self.instance, self.config.data["addr"],  self.config.data["port"], self.config.data["ssl"])

    __repr__ = __str__
