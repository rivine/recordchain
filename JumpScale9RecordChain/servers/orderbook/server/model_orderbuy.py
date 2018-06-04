

from js9 import j

JSBASE = j.application.jsbase_get_class()

SCHEMA="""
@url = threefoldtoken.order.buy
@name = orderbuy
comment = ""
currency_to_buy = "" (S)
currency_mine = (LS)    # which of my currencies I am selling (can be more than 1)
price_max =  (N)   # can be defined in any currency
expiration =  (D)  # can be defined as e.g. +1h
buy_from = (LS)    # list of wallet addresses which I want to buy from
secret = "" (S)    # the optional secret to use when doing a buy order, only relevant when buy_from used




"""

class model_orderbuy(JSBASE):
    
    def __init__(self):
        JSBASE.__init__(self)        
        self.namespace = "orderbuy"
        self.url = "threefoldtoken.order.buy"
        self.db = j.servers.gedis2.latest.db
        self.table = self.db.tables["orderbuy"]
        self.schema = self.table.schema

    def set(self,data_in):
        if j.servers.gedis2.latest.serializer:
            #e.g. for json
            ddict = j.servers.gedis2.latest.return_serializer.loads(data_in)
            obj = self.schema.get(data=ddict)
            data = obj.data
        else:
            id,data = j.data.serializer.msgpack.loads(data_in)

        res=self.table.set(data=data, id=id, hook=self.hook_set)
        if res.id == None:
            raise RuntimeError("cannot be None")

        if j.servers.gedis2.latest.serializer:
            return j.servers.gedis2.latest.return_serializer.dumps(res.ddict)
        else:
            return j.data.serializer.msgpack.dumps([res.id,res.data])

    def get(self, id):
        id=int(id.decode())
        obj = self.table.get(id=id, hook=self.hook_get)
        print("get")
        if j.servers.gedis2.latest.serializer:
            return j.servers.gedis2.latest.return_serializer.dumps(obj.ddict)
        else:
            return j.data.serializer.msgpack.dumps([obj.id,obj.data])

    def find(self,**args):
        return self.table.find(hook=self.hook_get,**args)
        
    def new(self):
        return self.table.new()

    def hook_set(self,obj,index=None):
        """
        before an object is set in the DB it will pass through this function, 
        this allows addional manipulation of object or security checks
        """
        #TODO:*1 remove owner_email_addr & secret
        return obj

    def hook_get(self,obj):
        """
        after an object is retreived from DB but before send to the consumer
        it will pass through this function, 
        this allows addional manipulation of object or security checks
        """
        #TODO:*1 remove owner_email_addr & secret
        return obj

