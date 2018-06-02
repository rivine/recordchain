

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
        #TODO:*1 put email in, check jwt against IYO

    def order_register(self,order):
        """
        ```in
        name = ""
        nr = 0 (I)
        ```
        ```out
        order_nr = 0 (I)
        ```
        
        """


    def test(self,name,nr,schema_out):      
        """
        some test method, which returns something easy

        ```in
        name = ""
        nr = 0 (I)
        ```

        ```out
        name = ""
        nr = 0 (I)
        list_int = (LI)        
        ```

        """  
        o=schema_out.new()
        o.name = name
        o.nr = nr
        # o.list_int = [1,2,3]

        return o
