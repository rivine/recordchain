import collections

class List0(collections.MutableSequence):

    def __init__(self, parentobj, parent,schema_property):
        # if type(l) is not list:
        #     raise ValueError()
        self._inner_list = []
        self._parent = parent
        self._parentobj = parentobj
        self.schema_property = schema_property
        self._copied = False

    def _copyFromParent(self):
        if not self._copied:
            self._inner_list = []
            for item in self._parent:
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
        value = self.schema_property.js9type.SUBTYPE.clean(value)
        self._inner_list.insert(index, value)
        self._parentobj.changed_list = True

    def __setitem__(self, index, value):
        self._copyFromParent()
        value = self.schema_property.js9type.SUBTYPE.clean(value)
        self._inner_list.__setitem__(index, value)
        self._parentobj.changed_list = True

    def __getitem__(self, index):
        if self._copied:
            return self._inner_list.__getitem__(index)
        else:
            return self._parent[index]

    @property
    def pylist(self):
        """
        python clean list
        """
        if self._copied:
            return self._inner_list
        else:
            res= [item for item in self._parent]
            return res
        

    def __repr__(self):
        out=""
        if self._copied:
            tointerate = self._inner_list
        else:
            tointerate = self._parent
        for item in tointerate:
            out+="- %s\n"%item
        return out
            

    __str__ = __repr__