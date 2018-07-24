
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

        self.tables = {}

    def table_get(self, schema, name=""):
        t = BCDBTable(self,schema=schema,name=name)
        self.tables[t.name]=t
        return t


    def tables_get(self,schema_path=""):
        """
        @PARAM schema_path if empty will look in current dir for all files starting with 'schema'
           if a directory will also walk over files in the directory
        """
        
        if schema_path=="":
            # j.data.schema.reset() #start from empty situation
            schema_path=j.sal.fs.getcwd()
        
        if j.sal.fs.isDir(schema_path):
            for path in j.sal.fs.listFilesInDir(schema_path, recursive=False, filter="schema*"):
                self.tables_get(schema_path=path)
        else:
            C=j.sal.fs.fileGetContents(schema_path)
            schemas = j.data.schema.schema_add(C)
            for schema in schemas:
                if schema.name!="":    
                    t = self.table_get(schema=schema,name=schema.name)
                # elif schema.url!="":
                #     t = self.table_get(schema=schema,name=schema.url.replace(".","_"))
                else:
                    raise RuntimeError("schema name should not be empty")
            
        return self.tables

    def destroy(self):
        self.zdb.destroy()
        