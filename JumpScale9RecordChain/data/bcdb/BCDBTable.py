
from js9 import j
from pprint import pprint as print
import time
import msgpack
from functools import reduce
import struct
JSBASE = j.application.jsbase_get_class()


class BCDBTable(JSBASE):

    def __init__(self,bcdb,schema,name=""):
        """
        """

        JSBASE.__init__(self)

        self.bcdb = bcdb

        s=bcdb.server

        self.name = name

        if j.data.types.string.check(schema):
            schema = j.data.schema.schema_from_text(schema)
        elif "_SCHEMA" in schema.__dict__:
            pass
        else:
            raise RuntimeError("input needs to be schema in text or obj format")

        if self.name=="":
            self.name = schema.name
            if not schema.name:
                raise RuntimeError("schema name cannot be empty")

        self.db =  self.bcdb.server.client_get(namespace=self.name, secret=s.config.data["adminsecret_"])

        self.schema = schema
        self.index = j.core.db  #only for now

        self._index_key = "index:%s:%s"%(self.db.instance,self.name)

        self.index_load()

    def index_delete(self):
        for key in self.index.keys(self._index_key+"*"):
            self.index.delete(key)

    def index_load(self):
        """
        """
        self.index_delete()
        self.logger.debug("build index for: %s"%self.name)
        def iload(id,data,result):
            meta, index,bdata = msgpack.unpackb(data)
            self._index(index,id)

        self.db.iterate(iload)
        self.logger.debug("build index done")

    def stop(self):
        # j.tools.prefab.local.zero_os.zos_db.stop(self.instance)
        pass 

    def destroy(self):
        self.stop()
        # j.sal.fs.removeDirTree(self.root_path)
        # ipath = j.dirs.VARDIR + "/zdb/index/%s.db" % self.instance
        # j.sal.fs.remove(ipath)
        # self._initdir()

    def set(self,data,id=0,hook=None):
        """
        if string -> will consider to be json
        if binary -> will consider data for capnp
        if obj -> will check of JSOBJ
        if ddict will put inside JSOBJ

        @RETURN JSOBJ
        
        """
        if  j.data.types.string.check(data):
            data = j.data.serializer.json.loads(data)
            obj = self.schema.get(data)
        elif j.data.types.bytes.check(data):
            obj = self.schema.get(data)
        elif "_JSOBJ" in data.__dict__:
            obj = data
            if id is 0 and obj.id is not 0:
                id=obj.id
        elif j.data.types.dict.check(data):
            obj = self.schema.get(data)
        else:
            raise RuntimeError("Cannot find data type, str,bin,obj or ddict is only supported")
        bdata = obj.data

        l=[]
        index={}
        for item in self.schema.index_list:
            r=eval("obj.%s"%item)
            if r:
                index[item]=r

        l=[0,index,bdata]
        data = msgpack.packb(l)

        if hook:
            obj = hook(obj,index)

        if id==0:
            #means a new one
            id = self.db.set(data)
            obj.id = id
        else:            
            self.db.set(data,id=id)

        self._index(index,id)
            
        return obj

    def _index(self,index,id):
        
        for key,item in index.items():
            if j.data.types.bytes.check(key):
                key=key.decode()
            key2=self._index_key+":%s"%key
            res = self.index.hget(key2,item)
            if res==None:
                res = struct.pack("<I",id)                
                self.index.hset(key2,item,res)
            else:
                res=self._index_get(res)
                if id not in res:
                    res.append(id)
                    res = msgpack.packb(res)
                    self.index.hset(key2,item,res)

    def _index_get(self,res):
        if len(res)==4:
            res =[struct.unpack("<I",res)[0]]
        else:
            res=msgpack.unpackb(res) #is already list
        return res

    def new(self):
        return self.schema.get()

    def get(self,id,capnp=False,hook=None):
        """
        @PARAM capnp if true will return data as capnp binary object
        @RETURN meta,index,obj 
        """

        data = self.db.get(id)

        if data==None:
            return None
        
        meta, index, bdata = msgpack.unpackb(data)

        if capnp:
            if hook:
                obj = hook(obj,index)
            return meta, index, bdata
        else:
            obj = self.schema.get(capnpbin=bdata)
            obj.id = id
            if hook:
                obj = hook(obj)
            return meta, index, obj

    def find(self,hook=None,**args):
        res=[]
        for key,val in args.items():
            indexkey=self._index_key+":%s"%key
            res2=[]
            if "*" in val:
                for item in self.index.hkeys(indexkey,val):
                    id=self.index.hget(indexkey,item)
                    id=struct.unpack("<I",id)[0]            
                    if id not in res2:
                        res2.append(id)
            else:
                id=self.index.hget(indexkey,val)
                if id is not None:
                    id=struct.unpack("<I",id)[0]            
                    if id not in res2:
                        res2.append(id)
            res.append(res2)

        res = [set(item) for item in res]
        res3 = reduce(set.intersection, res)
        res4=[]
        for item in res3:
            obj=self.get(item)[2]
            if hook:
                obj = hook(obj)
            res4.append(obj)     
        return res4



