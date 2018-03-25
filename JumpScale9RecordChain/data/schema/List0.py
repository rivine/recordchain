import collections

class List0(collections.MutableSequence):

    def __init__(self, parent=None, property_name = None):
        if type(l) is not list:
            raise ValueError()
        self._inner_list = []
        self._parent = parent
        self._property_name = property_name
        self._parentproperty = parent.__dict__[self._property_name]
        print("list ")
        from IPython import embed;embed(colors='Linux')
        s
        self._parentproperty_type = parent.schema.__dict__[self._property_name]
        self._copied = False

    def _copyFromParent(self):
        if not self._copied:
            for item in self._parentproperty:
                self._inner_list.append(item)
            self._copied = True

    def __len__(self):
        if self._copied:
            return len(self._inner_list)
        else:
            return len(self._parentproperty)

    def __delitem__(self, index):
        self._copyFromParent()
        self._inner_list.__delitem__(index )

    def insert(self, index, value):
        self._copyFromParent()
        self._inner_list.insert(index, value)

    def __setitem__(self, index, value):
        self._copyFromParent()
        self._inner_list.__setitem__(index, value)

    def __getitem__(self, index):
        if self._copied:
            return self._inner_list.__getitem__(index)
        else:
            return self._parentproperty[index]

    def __repr__(self):
        return str(self._inner_list)

    __str__ = __repr__