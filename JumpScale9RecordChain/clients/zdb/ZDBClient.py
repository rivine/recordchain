
from js9 import j
from pprint import pprint as print
import os
import struct
from .ZDBClientNS import ZDBClientNS

TEMPLATE = """
addr = "localhost"
port = "9900"
adminsecret_ = ""
secrets_ = ""
mode = "direct"
encryptionkey_ = ""
"""

JSConfigBase = j.tools.configmanager.base_class_config


class ZDBClient(JSConfigBase):

    def __init__(self, instance, data={}, parent=None, interactive=False,started=True):
        """
        is connection to ZDB

        - secret is also the name of the directory where zdb data is for this namespace/secret

        config params:
            secrets {str} -- format: $ns:$secret,... or $secret then will be same for all namespaces
            port {[int} -- (default: 9900)
            mode -- user,direct,seq(uential) see https://github.com/rivine/0-db/blob/master/README.md
            adminsecret does not have to be set, but when you want to create namespaces it is a must

        """
        self.init(instance=instance, data=data, parent=parent, interactive=interactive,started=started)

    def init(self, instance, data={}, parent=None, interactive=False, reset=False,started=True):

        JSConfigBase.__init__(self, instance=instance, data=data,
                              parent=parent, template=TEMPLATE, ui=None, interactive=interactive)
        
        # if not started:
        #     return

        self.mode = self.config.data["mode"]

        self.namespaces = {}

        #default namespace should always exist
            
    @property
    def adminsecret(self):        
        if self.config.data["adminsecret_"].strip() is not "":
            return self.config.data["adminsecret_"].strip()
        return ""


    @property
    def secrets(self):
        res={}
        if "," in self.config.data["secrets_"]:
            items = self.config.data["secrets_"].split(",")
            for item in items:
                if item.strip()=="":
                    continue
                nsname,secret = item.split(":")
                res[nsname.lower().strip()]=secret.strip()
        else:
            res["default"]=self.config.data["secrets_"].strip()
        return res
                
    def namespace_exists(self, name):
        try:
            self.namespace_system.redis.execute_command("NSINFO", name)
            return True
        except Exception as e:
            if not "Namespace not found" in str(e):
                raise RuntimeError("could not check namespace:%s, error:%s" % (name, e))
            return False

    def namespace_get(self,name):
        if not name in self.namespaces:
            self.namespaces[name] = ZDBClientNS(self,name)
        return self.namespaces[name]

    @property
    def namespace_system(self):
        return self.namespace_get("default")
        
    def namespace_new(self, name, secret="", maxsize=0):
        if self.namespace_exists(name):
            raise RuntimeError("namespace already exists:%s" % name)

        if secret is "" and "default" in self.secrets.keys():
            secret = self.secrets["default"]
        
        cl = self.namespace_system
        cl.redis.execute_command("NSNEW", name)
        if secret is not "":
            cl.redis.execute_command("NSSET", name, "password", secret)
            cl.redis.execute_command("NSSET", name, "public", "no")
        self.logger.debug("namespace:%s NEW" % name)

        if maxsize is not 0:
            cl.redis.execute_command("NSSET", name, "maxsize", maxsize)

        return self.namespace_get(name)