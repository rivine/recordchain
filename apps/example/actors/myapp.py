from js9 import j


JSBASE = j.application.jsbase_get_class()

class myapp(JSBASE):
    """
    """
    def __init__(self):
        JSBASE.__init__(self)


    def test_dns(self, obj, schema_out):
        """
        ```in
        !recordchain.digitalme.dnsrecord
        ```

        ```out
        !recordchain.digitalme.dnsrecord 
        ```
        """
        #TODO:*1 the obj in should be one populate at client, now is the properties of the obj so not ok
        from IPython import embed;embed(colors='Linux')

    def test_dns2(self, type,val, schema_out):
        """
        ```out
        [!recordchain.digitalme.dnsrecord]
        ```
        """
        o = schema_out.new()
        o.val = val
        o.type = type
        return o