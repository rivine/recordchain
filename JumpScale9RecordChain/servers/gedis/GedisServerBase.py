
from js9 import j

JSBASE = j.application.jsbase_get_class()


class GedisServerBase(JSBASE):
    def __init__(self):
        JSBASE.__init__(self)   

    def ping(self):
        return "PONG"

    def set(self, request=None, namespace=None, dbclient=None):
        """
        This is the basis for the generation of the template code. request,namespace and dbclient will be added in the template after server start.
        request is the data from the command.
        dbclient is the client used to connect to the backend.
        """

        if len(request) > 3:
            raise j.exceptions.RuntimeError('Unsupported command arguments')
        import asyncio
        loop = asyncio.get_event_loop()
        task = asyncio.async(dbclient.put(namespace, **{request[1].decode("utf-8"): request[2].decode("utf-8")}))
        return loop.run_until_complete(task)

    def get(self, request=None, namespace=None, dbclient=None):
        """
        This is the basis for the generation of the template code. request,namespace and dbclient will be added in the template after server start.
        request is the data from the command.
        dbclient is the client used to connect to the backend.
        """
        if len(request) > 2:
            raise j.exceptions.RuntimeError('Unsupported command arguments')
        import asyncio
        loop = asyncio.get_event_loop()
        task = asyncio.async(dbclient.get(namespace, request[1].decode("utf-8")))
        return loop.run_until_complete(task)
