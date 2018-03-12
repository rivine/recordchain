from js9 import j
# from collections import OrderedDict

from .ModelBase3 import ModelBase3


class ModelBaseData(ModelBase3):

    def __init__(self, key="", new=False, collection=None):
        super().__init__(key=key, new=new, collection=collection)
        self._data_schema = None
        self._data = None

    @property
    def data(self):
        if self._data is None:
            self._data = j.data.capnp3.getObj(self.dbobj.dataSchema, binaryData=self.dbobj.data)
        return self._data

    @property
    def dataSchema(self):
        return j.data.capnp3.getSchema(self.dbobj.dataSchema)

    @property
    def dataJSON(self):
        return j.data.capnp3.getJSON(self.data)

    @property
    def dataBinary(self):
        return j.data.capnp3.getBinaryData(self.data)


def getText(text):
    return str(object=text)


def getInt(nr):
    return int(nr)
