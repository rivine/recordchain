
from JumpScale9 import j

JSBASE = j.application.jsbase_get_class()

from .BCDBTable import BCDBTable


class BCDB(JSBASE):
    
    def __init__(self,zdbclient):
        self.zdbclient = zdbclient
        
        self.tables = {}

    def table_get(self, schema, name=""):
        if name in self.tables:
            return self.tables[name]

        t = BCDBTable(self,schema=schema,name=name)
        self.tables[name]=t
        return t


    def tables_get(self,schema_path=""):
        """
        @PARAM schema_path if empty will look in current dir for all files starting with 'schema'
           if a directory will also walk over files in the directory
        """
        
        if schema_path=="":
            # j.data.schema.reset() #start from empty situation
            schema_path=j.sal.fs.getcwd()

        if j.sal.fs.isDir(schema_path) and j.sal.fs.exists("%s/schemas"%(schema_path)):
            schema_path = "%s/schemas"%(schema_path)
        
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
        