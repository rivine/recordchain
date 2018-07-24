# BCDB


####  Basic Idea

- BCDB is a blockchain DB
- It uses tables as the basic storage unit
- Backend can be any DB (redis/zero-db)
- BCDB tables must have schemas (used to validate input)

- Schema
    - More info on schemas can be found [HERE](/JumpScale9RecordChain/data/schema/README.md)
    - Registered at the time of creating a table
        - You can specify schema string in the time of table creation
        - or you can provide a schema file containing many schemas
        - or you can provide a directory with multiple schema files
    - schema file is  `toml` file starts with `schema`
    - unlike SQL, schema is not a physical thing, it's an application layer

#### Running

**Pre-requisites**

- Install zerodb
    ```bash
    js9_code get --url="git@github.com:rivine/0-db.git"`
    cd $HOMEDIR/code/github/rivine/0-db && make && cp bin/zdb /opt/bin/`
    ```

**Start BCDB**
- You can provide an `adminsecret`
- If `reset` is set to `True`, old data is destroyed
- Start server ```j.data.bcdb.db_start(instance='example',adminsecret='my_secret', reset=False)```


**Get client**
- Use: ```db = j.data.bcdb.get("example")```

**Create db tables from schema file(s)**
- Assuming you have schema file(s) in `/home/hamdy/schemas` where every schema file starts with  the word `schema`
- Each must provide `@name` field and MUST not be empty as this will be taken as table name
- Use: 
    ```
    tables = db.tables_get('/home/hamdy/schemas')
    for table_name, table in tables.items():
        print(table_name)
        print(table_obj)
    ```

**Create db tables from schema strings**
- Define schemas as following:
    ```python
    schema = """
            @url = despiegk.test
            @name = TestObj
            llist2 = "" (LS)    
            name* = ""    
            email* = ""
            nr = 0
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
    
    schema2 = """
            @url = despiegk.test
            @name = TestObj2
            name* = ""    
            email* = ""
            nr = 0
            """
    ```
    
- create tables from the provided schemas as following 
    ```
    t = db.table_get(name="t1", schema=schema)
    t2 = db.table_get(name="t1", schema=schema2)
    ```

#### DB operations

**Populate a table with test data**

- Assuming we have a table object `t` coming from `t = db.table_get(name="t1", schema=schema)`
- This is an example 
    ```python
    for i in range(10):
        o = t.new() # new table
        o.llist.append(1)
        o.llist2.append("yes")
        o.llist2.append("no")
        o.llist3.append(1.2)
        o.U = 1.1
        o.nr = 1
        o.token_price = "10 EUR"
        o.description = "something"
        o.name = "name%s" % i
        o.email = "info%s@something.com" % i
        o2 = t.set(o)
        assert o2.id == i
    
    o3 = t.get(o2.id)
    assert o3.id == o2.id
    
    assert o3.ddict == o2.ddict
    assert o3.ddict == o.ddict
    ```

**Find operations on a table**
```python
res = t.find(name="name1", email="info2@something.com")
assert len(res) == 0

res = t.find(name="name2")
assert len(res) == 1
assert res[0].name == "name2"

res = t.find(name="name2", email="info2@something.com")
assert len(res) == 1
assert res[0].name == "name2"

o = res[0]

o.name = "name2"
assert o.changed_prop == False  # because data did not change, was already that data
o.name = "name3"
assert o.changed_prop == True  # now it really changed

assert o.ddict["name"] == "name3"
```
