from js9 import j

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

class GedisClient(JSConfigBase):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigBase.__init__(self, instance=instance, data=data,
                              parent=parent, template=TEMPLATE, interactive=interactive)
        self._redis = None

    @property
    def ssl_certfile_path(self):
        p = j.sal.fs.getDirName(self.config.path) + "cert.pem"
        if self.config.data["sslkey"]:
            return p

    @property
    def redis(self):
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
