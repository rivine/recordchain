

from js9 import j

JSBASE = j.application.jsbase_get_class()

class Wallet():
    
    def __init__(self):
        self.addr = ""
        self.email = ""
        self.jwt = ""    
    

class orderbook(JSBASE):
    
    def __init__(self):
        JSBASE.__init__(self)
        self.wallet= None
        self.orders = []



    def wallet_register(self,addr,jwt):
        self.wallet = Wallet()
        self.wallet.addr = addr
        self.wallet.jwt = jwt
        #TODO:*1 put email in from the jwt, check jwt against IYO

    def order_sell_register(self,order,schema_out):
        """
        ```in
        name = ""
        nr = 0 (I)
        ```
        ```out
        !threefoldtoken.order.sell     
        ```
        
        """
        o = schema_out.new()
        return o


