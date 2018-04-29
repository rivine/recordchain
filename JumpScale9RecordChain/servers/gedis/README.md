This module allow you to create a custom gevent server talking RESP (redis protocol)

To generate certificate and key 
```
openssl genrsa -out key.pem 2048
openssl req -new -x509 -key key.pem -out cert.pem -days 1095
```

## Server data

- `addr`: address of the server, defaults to `localhost`
- `port`: port of the server, defaults to `9900`
- `ssl`: use ssl, defaults to `False`
- `dbclient_instance`: instance of client to connect to backend, can be empty

## Example
```python
"""
Example server that only implements PING command
"""

from js9 import j

JSBASE = j.application.jsbase_get_class()


class GedisServerBase(JSBASE):

    def __init__(self):
        JSBASE.__init__(self)

    def ping(self):
        return "PONG"
```

The above represents a namespace in the gedis server. In each namespace we define the available commands which can only be used in that namespace.
In order to add new command, you need to do 2 things:

1. Inside your namespace class define a method that represents the logic of your command
2. add the namespace to the gedis server using `cmds_add`

The method needs to accepts 3 arguments `request`, `namespace`, `dbclient`:

- `request` is a list that contains the command name as first item and the optional extra arguments of the command in the rest of the list.
- `namespace` is the namespace specified above.
- `dbclient` is the client used to connect to the backend if needed.

For example adding a system namespace using [GedisServerBase](GedisServerBase.py):

```python
server = j.servers.gedis.get()
gedis.cmds_add('system', '/opt/code/github/rivine/recordchain/JumpScale9RecordChain/servers/gedis/GedisServerBase.py')
```

The generated code used will be stored in the gedis server directory in your config repo. You can check your config repo location using `j.tools.configmanager.path`, eg: `{configpath}/j.servers.gedis/{server instance}/{namespace}.py`. Example using the example above:

```python
from JumpScale9 import j

def ping(request, namespace, dbclient):
    return "PONG"

```

To test with redis client you can use jumpscale redis client as follows:

```python
In [1]: r = j.clients.redis.get('192.168.20.185', 5000, ssl=True, ssl_certfile='/tmp/cert.pem', ssl_keyfile='/tmp/key.pem')

In [2]: r.execute_command('system.ping') # {namespace}.{registered command in that namespace}
Out[2]: b'PONG'
```

Or using the gedis client:

```python
gcl = j.clients.gedis.get()
gcl.redis.execute_command('system.ping')
```

Client data:

- `addr`: address of the gedis server to connect to
- `password`: if needed authentication
- `port`: port of the gedis server to connect to
- `ssl`: use ssl, defaults to `False`
- `sslkey`: sslkey if needed
- `unixsocket`: optionally use a unix socket to connect to the server

Another option is to use the javascript client to execute the commands, see [docs](https://github.com/incubaid/redisjs).

## Working with a backend

By default gedis server isn't connected to any backend which is needed for storing and retrieving data from the gedis server. To add a backend to the gedis server you need to specify `dbclient_instance` in the server data. Using this parameter a client instance is created that connects to a running backend server. The user can then define methods like `put` and `get` in the specified namespace in accordance with the client.

In the following example we will showcase adding a gundb backend.

### Gundb backend integration

To setup a gundb client instance see the [docs](../../clients/gedis_backends/README.md). To start a gedis server check how [here](../Gundb/README.md).

The value of `dbclient_instance` should now be the instance name when starting the gedis server. The client is passed to each method in the namespace class and can be used as needed to connect to the running backend.

See [here](GedisServerBase.py) for implementation of `set` and `get` that works with Gundb client.

The generated code for that namespace will look like that:

```python
def get(request, namespace, dbclient):
    '''
    This is the basis for the generation of the template code. request,namespace and dbclient will be added in the template after server start.
request is the data from the command.
dbclient is the client used to connect to the backend.

    '''
    if len(request) > 2:
        raise j.exceptions.RuntimeError('Unsupported command arguments')
    import asyncio
    loop = asyncio.get_event_loop()
    task = asyncio.async(dbclient.get(namespace, request[1].decode("utf-8")))
    return loop.run_until_complete(task)


def set(request, namespace, dbclient):
    '''
    This is the basis for the generation of the template code. request,namespace and dbclient will be added in the template after server start.
request is the data from the command.
dbclient is the client used to connect to the backend.

    '''
    if len(request) > 3:
        raise j.exceptions.RuntimeError('Unsupported command arguments')
    import asyncio
    loop = asyncio.get_event_loop()
    task = asyncio.async(dbclient.put(namespace, **{request[1].decode("utf-8"): request[2].decode("utf-8")}))
    return loop.run_until_complete(task)
```

Now using the client it is possible to execute following commands:

```python
gcl.redis.execute_command('system.set', 'name', 'vito')
```

The command will add under `system` namespace key `name` with value `vito`. To get that value:

```python
result = gcl.redis.execute_command('system.get', 'name')
```