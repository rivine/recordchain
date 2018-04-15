

from js9 import j

JSBASE = j.application.jsbase_get_class()

class GedisServerExample(JSBASE):
    
    def __init__(self):
        JSBASE.__init__(self)

    def ping(self):
        return "PONG"

    def sum(self,a,b):
        """
        some a

        ```in
        a = (N)
        b = (N)
        ```

        some b
        """  
        pass
        return a+b          

    def sumb(self,a,b):
        """
        some a

        ```in
        a = (N)
        b = (N)
        ```

        ```out
        res = (N)
        ```

        some b
        """  
        pass
        return a+b          
