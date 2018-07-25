# BCDB


####  Basic Idea

- BCDB is a blockchain DB
- Backend can be any DB (redis/zero-db)
- It uses tables as the basic storage unit
- A BCDB table MUST follow certain schema
    - BCDB depends on [`j.data.schema`](schema.md) framework for Schemas
    - Schemas are in memory input validation layer (Not physical like SQL DBs)
    - By depending on `j.data.schema` frameowrk, you can create an object from certain schema, serialize it into `capnp/json` or you can
    deserialize `json/capnp` data into an object again.
    - `capnp` format is very useful for storing data in concise manner in `0-db`


## Running

###  Pre-requisites

**Install 0-DB**

```
j.servers.zdb.build()
```

**Start BCDB**

```
j.data.bcdb.db_start(instance='example',adminsecret='my_secret', reset=False)
```


**client**
```
db = j.data.bcdb.get("example")
```

### Create Schema and DB tables

- In any Schema **If you want a field to be indexed (can be searched for values ) you have to end it with `*` i.e `email* = (S)`**

**From Schema file(s)**


- create a `tmol` file(s) that **Startswith** `schema` i.e `schema_examples.toml`
- Example `schema.toml`
    ```
    # Wallet
    @url = threefoldtoken.wallet
    @name = wallet
    jwt = "" (S)                # JWT Token
    addr = ""                   # Address
    ipaddr = (ipaddr)           # IP Address
    email = "" (S)              # Email address
    username = "" (S)           # User name

    # Transaction
    @url = threefoldtoken.transaction
    @name = transaction
    buy_order_id = (I)          # id of buy order
    sell_order_id = (I)         # id of sell order
    amount_bought = (F)         # the trade amount
    currency = (S)              # the currency in which the transaction will happen
    total_price = (F)           # total price of the transaction
    state = (S)                 # state of the transaction new/pending/failed/succeeded
    buyer_wallet_addr = (S)     # Buyer wallet address
    seller_wallet_addr = (S)    # Seller Wallet address
    buyer_email_addr = (S)      # email addr used through IYO for the buyer
    seller_email_addr = (S)     # email addr used through IYO for the seller
    ```

- **`@name` field and MUST not be empty as this will be taken as table name**
- Load Schema file(s) from any path using:
    ```
    tables = db.tables_get('PATH-To-DIR-CONTAINING-SCHEMA-FILES')
    for table_name, table in tables.items():
        print(table_name)
        print(table_obj)
    ```

**Directly from schema strings**

- **`@name` field is not required, as table name is provided explicitly later**

- Define schemas as following:
    ```
    wallet_schema = """
    @url = threefoldtoken.wallet
    @name = wallet
    jwt = "" (S)                # JWT Token
    addr = ""                   # Address
    ipaddr = (ipaddr)           # IP Address
    email = "" (S)              # Email address
    username = "" (S)           # User name
    """

    transaction_schema = """
    @url = threefoldtoken.transaction
    @name = transaction
    buy_order_id = (I)          # id of buy order
    sell_order_id = (I)         # id of sell order
    amount_bought = (F)         # the trade amount
    currency = (S)              # the currency in which the transaction will happen
    total_price = (F)           # total price of the transaction
    state = (S)                 # state of the transaction new/pending/failed/succeeded
    buyer_wallet_addr = (S)     # Buyer wallet address
    seller_wallet_addr = (S)    # Seller Wallet address
    buyer_email_addr = (S)      # email addr used through IYO for the buyer
    seller_email_addr = (S)     # email addr used through IYO for the seller
    """

    wallet_table  = db.table_get(name="wallet", schema=wallet_schema)
    transaction_table = db.table_get(name="transaction", schema=transaction_schema)

    ```

### Full Example

**Notice that you can use `{table}.find` only on indexed fields `Ending with *`**

```
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
        """

schema2 = """
        @url = despiegk.test
        @name = TestObj2
        name* = ""
        email* = ""
        nr = 0
        """


t = db.table_get(name="t1", schema=schema)
t2 = db.table_get(name="t1", schema=schema2)

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
