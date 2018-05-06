import collections
from JumpScale9 import j
class List0(collections.MutableSequence):

    def __init__(self, parentobj, parent,schema_property):
        self._inner_list = []
        self._parent = parent
        self._parentobj = parentobj
        self.schema_property = schema_property
        self._pointer_schema = None
        self._copied = False

    def _copyFromParent(self):
        if not self._copied:
            self._inner_list = []
            for item in self._parent:
                if self.schema_property.pointer_type is None:
                    self._inner_list.append(item)
                else:
                    #create the subobject in the list
                    item = self.pointer_schema.get(capnpbin=item)
                    self._inner_list.append(item)
            self._copied = True

    def __len__(self):
        if self._copied:
            return len(self._inner_list)
        else:
            return len(self._parent)

    def __delitem__(self, index):
        self._copyFromParent()
        self._inner_list.__delitem__(index )
        self._parentobj.changed_list = True

    def insert(self, index, value):
        self._copyFromParent()
        if self.schema_property.pointer_type is None:
            value = self.schema_property.js9type.SUBTYPE.clean(value)
        else:
            if not "_JSOBJ" in value.__dict__:
                raise RuntimeError("need to insert JSOBJ, use .new() on list before inserting.")

        self._inner_list.insert(index, value)
        self._parentobj.changed_list = True

    def __setitem__(self, index, value):
        self._copyFromParent()
        if self.schema_property.pointer_type is None:
            value = self.schema_property.js9type.SUBTYPE.clean(value)
        else:
            if not "_JSOBJ" in value.__dict__:
                raise RuntimeError("need to insert JSOBJ, use .new() on list before inserting.")
        self._inner_list.__setitem__(index, value)
        self._parentobj.changed_list = True

    def __getitem__(self, index):
        if self.schema_property.pointer_type is not None:
            #means embedded objects, will expand
            self._copyFromParent()
        if self._copied:
            return self._inner_list.__getitem__(index)
        else:            
            return self._parent[index]

    @property
    def pylist(self):
        """
        python clean list
        """
        if self.schema_property.pointer_type is not None:
            #means embedded objects, will expand
            self._copyFromParent()        
        if self._copied:
            if self.schema_property.pointer_type is None:
                return self._inner_list
            else:
                return [item.ddict for item in self._inner_list]                
        else:
            res= [item for item in self._parent]
            return res
        
    def new(self):
        """
        return new subitem, only relevant when there are pointer_types used
        """
        s=self.pointer_schema.new()
        self.append(s)
        return s

    @property
    def pointer_schema(self):
        if self._pointer_schema is None:
            if self.schema_property.pointer_type==None:
                raise RuntimeError("can only be used when pointer_types used")
            s =  j.data.schema.schema_from_url(self.schema_property.pointer_type)
            self._pointer_schema = s
        return self._pointer_schema

    def __repr__(self):
        if self.schema_property.pointer_type is not None:
            #means embedded objects, will expand
            self._copyFromParent()                
        out=""
        if self._copied:
            tointerate = self._inner_list
        else:
            tointerate = self._parent
        for item in tointerate:
            out+="- %s\n"%item
        if out.strip()=="":
            return "[]"
        return out
            

    __str__ = __repr__