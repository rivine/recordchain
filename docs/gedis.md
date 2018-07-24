# Gedis

Application server which amongst others use the `redis protocol`
and have their own set of `custom redis commands`

Functions of gedis

- interfaces
    - redis commands (tcp)
    - websockets (to use from javascript library)
- super easy to create
    - goal is no boilerplate code, all code gets generated
    - schema's are in 


You create an `app/instance server` and you can get a `client` that can connect to your app
and execute the commands easily

A `Gedis` server uses [BCDB DB](/JumpScale9RecordChain/data/bcdb/README.md)
that saysm, you can add `schema` toml files to your generated server directory and 
DB tables will be created for each schema you have.
This is the `Model layer`


### installation

see [recordchain_install](/recordchain_install.md)

```bash
#build zdb
js9 'j.servers.zdb.build()'
```

### Test

```bash
cd $HOMEDIR/code/github/rivine/recordchain/apps/orderbook/
python3 test.py
```

### Running

**Hello world example**
Get the `example` app in [HERE](/JumpScale9RecordChain/apps/)

```python
#Configure & Run server
j.servers.gedis.get('example').start(background=False, reset=True)
#Configure & Get client 
client = j.clients.gedis.get('example', reset=True)
#execute system command ping
assert client.system.ping()==b'PONG'
```

- Instance name here refers to application name. In this case our app is called `example`
- During configuration phase for this helloworld example, leve `apps_dir` empty for both server & client
This ensures that apps dir will be set to `/JumpScale9RecordChain/apps/` and that the `helloworld` app called `example` will be loaded from there
you can change this if you want to create/load apps elsewhere

### General Picture for how Server & client work and comunicate

**Server**

- Generates code at `/opt/var/codegen/{instance}/server`
- Copies `system.py` to `/opt/var/codegen/{instance}/server` which contains system redis commands like `ping`
- Load and register commands/functions from `system.py` as well as other modules in `{apps_dir}/{instance}`
- collect schemas in toml file(s) that starts with `schema_` in `apps_dir/{instance}`
- For each schema collected 
    - create a schema file for that schema in `/opt/var/codegen/schema`
    - load schema in memory
    - create db table with the same name as schema name
    - create model file names `model_{schema_name}.py` under `/opt/var/codegen/{instance}/server` and add it to dictionary
    `j.servers.gedis.latest.db.tables`.
    - models allow for `CRUD` operations on a table

**Client**
- Creates `/opt/var/codegen/{instance}/client` directory in the 1st time
- Fetch server for all schemas loaded inside it
- Create `/opt/var/codegen/{instance}/server`
- For each schema in loaded schemas
    - create a schema file for that schema in `/opt/var/codegen/schema`
    - load schema in memory
    - create model file names `model_{schema_name}.py` under `apps_dir/{instance}/client` and add it to client instance
    in `models` property so it can be accessed through `client.models.{model_name}`
- Fetch server for each registered command
- For each namespace registered in server
    - create `/opt/var/codegen/{instance}/client/cmds_{instance}_{namespace}.py` file containign all commands in that name space
    - for each command, make sure if `schema_in` for a command is provided to expand its properties in the client command function arguments


### Make your own app

- **Make your own app**
    ```
    app = j.servers.gedis.get(instance='my_app')
    app.start(background=True, reset=True)
    ```

    OR configure it directly like

    ```
    server = j.servers.gedis.configure(
            instance="example",
            port=5000,
            host="127.0.0.1",
            secret="",
            apps_dir=''
        )

    server.start()
    ```

- **Get Gedis python client**

    - You can use any redis library to connect to your app and execute commands
    - or you use the client from jumpscale `j.clients.gedis.get({instance}, reset=True/False)`

- **Adding models to your server** 
    - In your `{apps_dir}/{instance_name}` you can add some `toml` files MUST start with `schema`.
    - These schema files represent the `Model` layer in an `MVC` framework these are your models
    - example [HERE](https://github.com/rivine/recordchain/blob/master/JumpScale9RecordChain/apps/orderbook/schema.toml) 

- **Add custom redis commands / API**
    - In your `{apps_dir}/{instance_name}` add a python file
    - Example:
        - file `system.py`
            ```python
            from js9 import j
        
            JSBASE = j.application.jsbase_get_class()
            
            class system(JSBASE):
                
                def __init__(self):
                    JSBASE.__init__(self)
            
                def ping(self):
                    return "PONG"
            
                def ping_bool(self):
                    return True
            ```
         
        - each function is registered in client as a redis command under `client.system.{function name}`
        i.e `client.system.ping()` or  `client.system.ping_bool()`

    - How to define a custom redis command:
        - If you have simple function with no input and returning simple data type ay like boolean, list, string, .. in this case no need to do anything, just return directly as in `ping`
            ```python
              def ping(self):
                    return "PONG"
            
                def ping_bool(self):
                    return True
            ```
        - If you have inputs, you must define `in` schema in your docstring and if you have output schema, you must
        define `out` schema in docstring as well as a `schema_out` argument to the function
            ```python
               def test(self,name,nr,schema_out):
                """
                some test method, which returns something easy
                ```in
                name = "" (S)
                nr = 0 (I)
                ```
                ```out
                name = "" (S)
                nr = 0 (I)
                ```
                """
                o=schema_out.new()
                o.name = name
                o.nr = nr
                return o
            ```

### Websockets support

```javascript
<script type="text/javascript">

  socket = new WebSocket("ws://172.17.0.2:9901/");
  result = null

  socket.onopen = function() {
	console.log('connected')
	socket.send('system.ping')
        
}; 
  socket.onmessage = function(e) {
	console.log(e.data)
}

</script>

```
### Configuring Gedis Server for web

**general idea**

- Install caddy webserver with wsproxy plugin which forwards traffic to redis
- Use a javascript redis client to make a socket.io connection with wsproxy

**Configuration Details**

- Install `caddy`
    - `j.tools.prefab.local.runtimes.golang.install()`
    - Get [caddyman](https://github.com/Incubaid/caddyman)
    - Install caddy and `wsproxy` plugin using `./caddyman install wsproxy`
- Configuring caddy
    - create a directory called `static` somewhere to hold static contents of caddy
    - create `caddy.conf` file - Replace `{PATH-TO-STATIC-DIR}` with the path of static dir
        ```
        http://{IP}:{PORT} {
            root  {PATH-TO-STATIC-DIR}
            wsproxy     /redis     localhost:9900
        }
        ```
    - under {PATH-TO-STATIC-DIR} create a file `client.js` with following content but remeber to change `SERVER_DOMAIN` and `SERVER_PORT` values
    to match `{IP}` & `PORT` values that caddy listens on

        ```
        function loadScript(url, callback){
            var script = document.createElement("script")
            script.type = "text/javascript";

            if (script.readyState){  //IE
                script.onreadystatechange = function(){
                    if (script.readyState == "loaded" ||
                            script.readyState == "complete"){
                        script.onreadystatechange = null;
                        callback();
                    }
                };
            } else {  //Others
                script.onload = function(){
                    callback();
                };
            }

            script.src = url;
            document.getElementsByTagName("head")[0].appendChild(script);
        }


        loadScript("https://cdn.rawgit.com/arahmanhamdy/redisjs/master/build/redisjs.min.js", function(){
                SERVER_DOMAIN = "172.17.0.2"
            SERVER_PORT = "8200"
            redis = null

            function successCallback(conn){
                console.log('Connected')
                redis = conn
                redis["system.get_web_client"]((res) => {
                     eval(res)
                })

            }

            const redisConnection = new RedisConnection(SERVER_DOMAIN + ":" + SERVER_PORT+ "/redis");
            redisConnection.connect(successCallback, function(err){console.log(err)});


        });
        ```
- run caddy using `/home/{user}/go/bin/caddy -conf caddy.conf`

**Web browser**
- Include the following script in your web page
    ```
    <script type="text/javascript" src="http://{IP}:{PORT}/client.js"> </script>
    ```
- Now you can execute commands i.e `Commands.system.ping(function(res){console.log(res)})`
