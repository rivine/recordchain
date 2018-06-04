## recordchain for python

- gevent redis server
- blockchain logic
- zerodb client


### installation

```bash
js9_code get --url="git@github.com:rivine/recordchain.git"
cd $HOMEDIR/code/github/rivine/recordchain
sh install.sh
```

### Code Generations Path

**By default you will find code generated under `/opt/var/codegen/gedis`**

- Example For instance called `test` you'll find code under
    - /opt/var/codegen/gedis/{test}/server
    -  /opt/var/codegen/gedis/{test}/client
    -  /opt/var/codegen/gedis/{test}/schema

### Server

- **Start** *(In Tmux)*

    ```
    j.servers.gedis2.start(instance="test", schema_path="/opt/code/github/rivine/recordchain/JumpScale9RecordChain/servers/gedis2/EXAMPLE/", background=True)
    ```

- **Args**
   - *instance*: instance name
   - *schema_path*: dir containing `schema.toml`

### client
```
In [6]: cl = j.clients.gedis2.get('test')
In [7]: cl.redis.execute_command('system.ping')
Out[7]: b'PONG'
```

or

```
cl = j.clients.gedis2.configure(instance="test",ipaddr="localhost", \
    port=5000, password="", unixsocket="",
    ssl=False, ssl_keyfile=None, ssl_certfile=None)

In [7]: cl.system.ping()
Out[7]: b'PONG'
```

### Tests

**CLient**
```
j.clients.gedis2.test()

```

**Server**

```
j.servers.gedis2.test()

```
