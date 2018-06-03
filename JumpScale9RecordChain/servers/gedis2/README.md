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

ServerClass = j.servers.gedis2.baseclass_get()

def ping(request):
    return "PONG"

def witherror(request):
    raise RuntimeError("some error") #only the error message will be forwarded to the client


if __name__ == "__main__":
    server = ServerClass(host='localhost', port=6379, keyfile="/tmp/key.pem", certfile="/tmp/cert.pem"))
    server.register_command('PING', ping)
    server.start()
```


To test with redis client you can use jumpscale redis client as follows
```
In [1]: r = j.clients.redis.get('192.168.20.185', 5000, ssl=True, ssl_certfile='/tmp/cert.pem', ssl_keyfile='/tmp/key.pem')

In [2]: r.execute_command('PING')
Out[2]: True
```