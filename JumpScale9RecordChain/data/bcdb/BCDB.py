
from JumpScale9 import j


TEMPLATE = """
zdb_port = "9901"
zdb_adminsecret_ = ""
"""

JSConfigBase = j.tools.configmanager.base_class_config

from .BCDBTable import BCDBTable


class BCDB(JSConfigBase):
    
    def __init__(self,instance, data={}, parent=None, interactive=False, reset=False):
        JSConfigBase.__init__(self, instance=instance, data=data,
                              parent=parent, interactive=interactive, template=TEMPLATE)      

        self.db = j.clients.zdb.get(instance=instance)

    def table_get(self,name,schema):
        return BCDBTable(self,name,schema)
