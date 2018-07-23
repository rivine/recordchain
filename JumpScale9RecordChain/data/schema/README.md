## Schema

An Input validation & conversion layer

#### Basic Idea

- providing a schema, you can create an object from it. then set fields inside the object
with a data of a proper data type that matches the data type of that field in the schema
These objects can be serialized/deserialized into/from `json`, `capnp` , or `yaml`
you can later on save these objects into DB 

- The most interesting thing here is the set of data types supported by schema

- Each schema can have a URL, then you can get that schema by its registered URL
- Each schema can have a name
- You can load schemas from a string, from a `toml` file starting with the word `schema*` or from a dir containing schema file(s)


#### Schema Data types
- Schema supports many many data types listed in `j.data.types`
- Schema parser makes its best to identify the data type if not provided
- some of these data types are
    * I: Integer
    * F: Float
    * S: String
    * O: Object (another schema)
    * L: List
    * L(I): List Integer
    * L(F): List Float
    * L(S): List String
    * L(O): List of objects
    * D: Date
    * N: Numeric i.e "10 EUR"

#### Schema Examples

```toml
@url = test.gedis.cmd
@name = any
name = "" 
comment = "" # type inference will set type to (String)
schemacode = ""

@url = test.gedis.serverschema
@name = cmds
cmds = (LO) !test.gedis.cmd

@url = test.gedis.cmd1
@name = cmd
cmd = (O) !test.gedis.cmd # Type Object. then you provide the URL of the schema that it refers to
cmd2 = (O) !test.gedis.cmd
```

```toml
@url = threefoldtoken.wallet
@name = wallet
jwt = "" (S)                # JWT Token
addr = ""                   # Address
ipaddr = (ipaddr)           # IP Address
email = "" (S)              # Email address
username = "" (S)           # User name
```

### Code generation

Each registered schema in jumpscale, is turned into a model object that is generated
and saved under `/opt/var/codegen/schema/{schema_url}.py` with replacing `(.)` in URL
to `_` so for a schema with `threefoldtoken.wallet` URL the following schema file
is created `/opt/var/codegen/schema/threefoldtoken_wallet.py` and loaded into memory
to allow manipulations and dynamic functions/operations on schema fields

The generated file is created from a template file in `schema/templates/template_obj.py`

#### Code

**Test everything works fine**

```python
    j.data.schema.test()
```


**Add/Register schema from a string**

- Use `j.data.schema.schema_add(schema_string)` which returns list of added schemas objects

- ```python
    schema = """
    @url = threefoldtoken.wallet
    @name = wallet
    jwt = "" (S)                # JWT Token
    addr = ""                   # Address
    ipaddr = (ipaddr)           # IP Address
    email = "" (S)              # Email address
    username = "" (S)           # User name
    payment = (N)               # Registration fees
    """ 
    # List of schemas returned from 
    schemas = j.data.schema.schema_add(schema)
    schema = schemas[0]
    
    print(schema) 
    
    prop:jwt                       (string)   default:""
    prop:addr                      (string)   default:""
    prop:ipaddr                    (ipaddr)
    prop:email                     (string)   default:""
    prop:username                  (string)   default:""
    prop:payment                   (numeric)   default:b'\x01\x97\x00\x00\x00\x00\x00\x00\x00\x00'
    ```

**Get a registered schema from a URL**
- Use `j.data.schema.schema_from_url(url)`

- ```python
    schema = j.data.schema.schema_from_url("threefoldtoken.wallet")
    print(schema)
    prop:jwt                       (string)   default:""
    prop:addr                      (string)   default:""
    prop:ipaddr                    (ipaddr)
    prop:email                     (string)   default:""
    prop:username                  (string)   default:""
    prop:payment                   (numeric)   default:b'\x01\x97\x00\x00\x00\x00\x00\x00\x00\x00'
  ```

**Create new Object**
- ```python
    obj = schema.new()
    print(obj)
    
    {
         "addr": "",
         "email": "",
         "ipaddr": "",
         "jwt": "",
         "payment": "0.0",
         "username": ""
    }
  
    obj.jwt = "lovely-jwt"
    obj.addr = "wallet-addr"
    obj.ipaddr = '8.8.8.8'
    obj.username = 'hamdy'
    obj.email = 'hamdy@greenitglobe.com'
    obj.payment = j.data.types.numeric.clean('20eur')
  
    print(obj)
  
    {
     "addr": "wallet-addr",
     "email": "hamdy@greenitglobe.com",
     "ipaddr": "8.8.8.8",
     "jwt": "lovely-jwt",
     "payment": "20.0 EUR",
     "username": "hamdy"
    }

   ```
   
**Object as dictionary**

- ```python
    # object as dict
    print(obj.ddict)
    
    {'jwt': 'lovely-jwt', 'addr': 'wallet-addr', 'ipaddr': '8.8.8.8', 'email': 'hamdy@greenitglobe.com', 'username': 'hamdy', 'payment': b'\x010\x00\x00\x00\x00\x00\x004@'}
    
    # object as human readable
    print(obj.ddict_hr)
  
    {'jwt': 'lovely-jwt', 'addr': 'wallet-addr', 'ipaddr': '8.8.8.8', 'email': 'hamdy@greenitglobe.com', 'username': 'hamdy', 'payment': '20.0 EUR'}  
 
  ```
  
**Serialize objects**

- JSON: ```obj.json```
- MSGPACK: ```obj.msgpack```
- CAPNP: ```obj.data```

**Deserialize from capnp**
- ```python
    data = obj.data
    print(data)
    b'\x10\x12@\x06\x11\x15Z\x11\x19b\x11\x1dB\x11\x1d\xba\x11%2\x11%R\xfflovely-j\x00\x03wt\xffwallet-a\x00\x07ddr\x7f8.8.8.8\xffhamdy@gr\x01eenitglo?be.com\x1fhamdy\x03\x010\x034@'
    
    schema = j.data.schema.schema_from_url("threefoldtoken.wallet")
    obj = schema.get(capnpbin=data)
    print(obj)

    {
     "addr": "wallet-addr",
     "email": "hamdy@greenitglobe.com",
     "ipaddr": "8.8.8.8",
     "jwt": "lovely-jwt",
     "payment": "20.0 EUR",
     "username": "hamdy"
    }

   ```

**Numeric / Curency Data type manipulation**
- When you define a field of type `j.data.types.numeric` or `(N)` you get extra currency conversion functions withput effort
- ```python
    print(obj.payment_eur)
    20.0

    print(obj.payment_usd)
    23.27752159572066

    print(obj.payment_cur('aed'))
    85.49130700956007
  ```

**Examplea**
```python
    def test(self):
        """
        js9 'j.data.schema.test()'
        """
        self.test1()
        self.test2()
        self.test3()

    def test1(self):
        """
        js9 'j.data.schema.test1()'
        """
        schema = """
        @url = despiegk.test
        @name = TestObj
        llist2 = "" (LS) #L means = list, S=String        
        nr = 4
        date_start = 0 (D)
        description = ""
        token_price = "10 USD" (N)
        cost_estimate:hw_cost = 0.0 #this is a comment
        llist = []
        llist3 = "1,2,3" (LF)
        llist4 = "1,2,3" (L)
        llist5 = "1,2,3" (LI)
        U = 0.0
        #pool_type = "managed,unmanaged" (E)  #NOT DONE FOR NOW
        """

        s = j.data.schema.schema_from_text(schema)
        print(s)

        o = s.get()

        o.llist.append(1)
        o.llist2.append("yes")
        o.llist2.append("no")
        o.llist3.append(1.2)
        o.llist4.append(1)
        o.llist5.append(1)
        o.llist5.append(2)
        o.U = 1.1
        o.nr = 1
        o.token_price = "10 EUR"
        o.description = "something"

        o.cobj

        schema = """
        @url = despiegk.test2
        @name = TestObj
        llist2 = "" (LS)        
        nr = 4
        date_start = 0 (D)
        description = ""
        token_price = "10 USD" (N)
        cost_estimate:hw_cost = 0.0 #this is a comment
        llist = []

        @url = despiegk.test3
        @name = TestObj2
        llist = []
        description = ""
        """
        j.data.schema.schema_add(schema)
        s1 = self.schema_from_url("despiegk.test2")
        s2 = self.schema_from_url("despiegk.test3")

        o1 = s1.get()
        o2 = s2.get()
        o2.llist.append("1")

        print("TEST 1 OK")

    def test2(self):
        """
        js9 'j.data.schema.test2()'
        """
        schema0 = """
        @url = despiegk.test.group
        @name = Group
        description = ""
        llist = "" (LO) !despiegk.test.users
        listnum = "" (LI)
        """

        schema1 = """
        @url = despiegk.test.users
        @name = User
        nr = 4
        date_start = 0 (D)
        description = ""
        token_price = "10 USD" (N)
        cost_estimate:hw_cost = 0.0 (N) #this is a comment
        """

        s1 = self.schema_from_text(schema1)
        s0 = self.schema_from_text(schema0)

        print(s0)
        o = s1.get()

        print(s1.capnp_schema)
        print(s0.capnp_schema)

        print("TEST 2 OK")


    def test3(self):
        """
        js9 'j.data.schema.test3()'

        simple embedded schema

        """
        SCHEMA = """
        @url = jumpscale.gedis.cmd
        @name = GedisCmd
        name = ""
        comment = ""
        schemacode = ""

        @url = jumpscale.gedis.serverschema
        @name = GedisServerSchema
        cmds = (LO) !jumpscale.gedis.cmd

        @url = jumpscale.gedis.cmd1
        @name = GedisServerCmd1
        cmd = (O) !jumpscale.gedis.cmd
        cmd2 = (O) !jumpscale.gedis.cmd
        
        """
        self.schema_add(SCHEMA)
        s1 = self.schema_from_url("jumpscale.gedis.cmd")
        s2 = self.schema_from_url("jumpscale.gedis.serverschema")
        s3 = self.schema_from_url("jumpscale.gedis.cmd1")

        o = s2.get()
        for i in range(4):
            oo = o.cmds.new()
            oo.name = "test%s"%i

        assert o.cmds[2].name=="test2" 
        o.cmds[2].name="testxx"
        assert o.cmds[2].name=="testxx" 

        bdata = o.data

        o2 = s2.get(capnpbin=bdata)

        assert o.ddict == o2.ddict

        print (o.data)

        o3 = s3.get()
        o3.cmd.name = "test"
        o3.cmd2.name = "test"
        assert o3.cmd.name == "test"
        assert o3.cmd2.name == "test"

        bdata = o3.data
        o4 = s3.get(capnpbin=bdata)
        assert o4.ddict == o3.ddict

        assert o3.data == o4.data

        print("TEST 3 OK")
```

