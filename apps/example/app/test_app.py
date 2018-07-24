from js9 import j


JSBASE = j.application.jsbase_get_class()

class test_app(JSBASE):
    """
    """
    def __init__(self):
        JSBASE.__init__(self)


    def test(self, wallet, schema_out):
        """
        ```in
        !recordchain.digitalme.dnsrecord
        ```

        ```out
        !recordchain.digitalme.dnsrecord
        ```
        """
        from IPython import embed;embed(colors='Linux')

