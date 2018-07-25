

from js9 import j

JSBASE = j.application.jsbase_get_class()

SCHEMA="""
{{obj.text}}
"""

class model(JSBASE):
    
    def __init__(self,client):
        JSBASE.__init__(self)        
        self.name = "{{obj.name}}"
        self.url = "{{obj.url}}"
        self.schema = j.data.schema.schema_from_url(self.url)
        self.client = client
        self.redis = client.redis

    def set(self,obj):
        bdata=j.data.serializer.msgpack.dumps([obj.id,obj.data])
        res = self.redis.execute_command("model_%s.set"%self.name,bdata)
        id,_= j.data.serializer.msgpack.loads(res)
        obj.id = id
        return obj

    def get(self,id):
        res = self.redis.execute_command("model_%s.get"%self.name,str(id))
        id,data=j.data.serializer.msgpack.loads(res)
        obj=self.schema.get(capnpbin=data)
        obj.id = id
        return obj

    def find(self, total_items_in_page=20, page_number=1, only_fields=[], {{find_args}}):
        items = self.redis.execute_command("model_%s.find"%self.name, total_items_in_page, page_number, only_fields, {{kwargs}})
        items = j.data.serializer.msgpack.loads(items)
        result = []

        for item in items:
            id, data = j.data.serializer.msgpack.loads(item)
            obj = self.schema.get(capnpbin=data)
            obj.id = id
            result.append(obj)
        return result

    def new(self):
        return self.schema.new()
