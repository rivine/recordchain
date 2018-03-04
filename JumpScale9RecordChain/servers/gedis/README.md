This module allow you to create a custom gevent server talking RESP (redis protocol)


## Example
```python
"""
Example server that only implements PING command
"""

from js9 import j

ServerClass = j.services.gedis.get_base_class()

def ping(request, response):
    response.encode("PONG")

if __name__ == "__main__":
    server = ServerClass(host='localhost', port=6379)
    server.register_command('PING', ping)
    server.start()
```

In order to add new command, you need to do 2 things:

1. define a method that represent the logic of your command
2. register the command and the callback using `register_command`

The method needs to accepts 2 arguments, `request` and `response`.

- `request` is a list that contains the command name as first item and the optional extra arguments of the command in the rest of the list.
- `response` is an object that has 3 methods that you need to use to rend response to the client
     - status: to send some status back to the client
     - error: to notify an error
     - encode: to write any type of data