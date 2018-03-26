This module allow you to create a custom gevent server talking RESP (redis protocol)

To generate certificate and key 
```
openssl genrsa -out key.pem 2048
openssl req -new -x509 -key key.pem -out cert.pem -days 1095
```
## Example
```python
"""
Example server that only implements PING command
"""

from js9 import j

ServerClass = j.servers.gedis.get_base_class()

def ping(request):
    return "PONG"

def witherror(request):
    raise RuntimeError("some error") #only the error message will be forwarded to the client


if __name__ == "__main__":
    server = ServerClass(host='localhost', port=6379, keyfile="/tmp/key.pem", certfile="/tmp/cert.pem"))
    server.register_command('PING', ping)
    server.start()
```

In order to add new command, you need to do 2 things:

1. define a method that represent the logic of your command
2. register the command and the callback using `register_command`
3. can also create additional methods on server class, will be auto registered

The method needs to accepts 1 argument = `request`

- `request` is a list that contains the command name as first item and the optional extra arguments of the command in the rest of the list.

To test with redis client you can use jumpscale redis client as follows
```
In [1]: r = j.clients.redis.get('192.168.20.185', 5000, ssl=True, ssl_certfile='/tmp/cert.pem', ssl_keyfile='/tmp/key.pem')

In [2]: r.execute_command('PING')
Out[2]: True
```