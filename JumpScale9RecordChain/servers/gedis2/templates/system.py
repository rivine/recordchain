

from js9 import j

JSBASE = j.application.jsbase_get_class()

class system(JSBASE):
    
    def __init__(self):
        JSBASE.__init__(self)

    def ping(self):
        return "PONG"

    def core_schemas_get(self):
        """
        return all core schemas as understood by the server, is as text, can be processed by j.data.schema

        ```out
        res = [] (LS)
        ```

        """
        for key,item in j.data.schema.schemas.items():
            print("core_schemas_get")
            from IPython import embed;embed(colors='Linux')
            k
        return a+b             

    def api_meta(self):
        """
        return the api meta information

        ```out
        res = (O) !jumpscale.gedis.api
        ```

        """  
        s=j.servers.gedis.latest
        for key,item in s.items():
            print("api_meta")
            from IPython import embed;embed(colors='Linux')
            k        
        pass
        return a+b          
