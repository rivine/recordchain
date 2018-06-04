

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
        self.orders = [] #TODO:*1 needs to be put on e.g. server  (WRONG)



    def wallet_register(self,addr,jwt,ipaddr,schema_out):
        """
        ```in
        addr = "" (S)
        jwt = "" (S)  
        ipaddr = "" (S)
        ```
        """        
        self.wallet = Wallet()
        self.wallet.addr = addr
        self.wallet.jwt = jwt
        #TODO:*1 put email in from the jwt, check jwt against IYO

    def order_sell_register(self,order,schema_out):
        """
        ```in
        !threefoldtoken.order.sell     
        ```
        ```out
        !threefoldtoken.order.sell     
        ```
        
        """
        o = schema_out.new()  #TODO:*1 fix
        return o

    def order_buy_register(self,order,schema_out):
        """
        ```in
        !threefoldtoken.order.buy     
        ```
        ```out
        !threefoldtoken.order.buy     
        ```
        
        """
        o = schema_out.new()  #TODO:*1 fix
        return o

    def order_buy_match(self,order_id, schema_out):
        pass
