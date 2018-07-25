## Orderbook

Orderbook is a Gedis app, that says you need to be familiar with
these topics before you can work with orderbook

- [Schemas](JumpScale9RecordChain/data/schema/README.md)
- [BCDB database](JumpScale9RecordChain/data/bcdb/README.md)
- [gedis Framework](JumpScale9RecordChain/servers/gedis/README.md)

# Specs

- Read about specs [HERE](JumpScale9RecordChain/apps/orderbook/specs.md)


# Orderbook

- #### Start server
    - Make sure in config to leave `app_dir` empty to load ordrbook from `JumpScale9RecordChain/apps/orderbook`
    - Orderbook is an instance of gedis and you can start server using
        ```python
        server = j.servers.gedis.get('orderbook')
        server.start()
        ```

- #### Start client
    ```python
    client = j.clients.gedis.get('orderbook')
    ```
- ####  USing client
    
    - **Test client working**
        - Issue the command
            ```python
            client.system.ping()
            ```
        - Result shoule be `PONG`

    - **Get a valid Itsyouonline JWT Token**

        ```python
        iyo_client = j.clients.itsyouonline.get()
        jwt = iyo_client.jwt
        ```
    
    -  **Client Login/Register client wallet**
        ```python
          client.order_book.login(jwt=jwt, ipaddr='my-wallet-ip', addr='my-wallet-addr')

        ```
    - **Operations on orders with default values** `client.{operation}`
        - **`WARNING`** : 
            - when adding/updating an order, if `approved` field is set to `True`, then order is final
            and can no more be edited and will start to be eligible for matching against other
            orders.
            - Non `approved` orders will not be matched
        - **API**
            - **`login(jwt='', addr='', ipaddr='', email='', username='')`**
                - *Params*:
                    - consumes all params of a [threefoldtoken.wallet](https://github.com/rivine/recordchain/blob/master/JumpScale9RecordChain/apps/orderbook/schema.toml#L32) object
                    
            - **`add_buy_order(comment='', currency_to_buy='', price_max='0.0', amount=0.0, expiration=0, secret='', approved=False, currency_mine=[  ], buy_from=[  ])`**
                - *params*:
                    - consumes all the params of [threefoldtoken.order.buy.create](https://github.com/rivine/recordchain/blob/master/JumpScale9RecordChain/apps/orderbook/schema_crud.toml#L43) object
                    
            - **`update_sell_order(comment='', currency_to_sell='', price_min='0.0', amount=0.0, expiration=0, approved=False, id=0, currency_accept=[  ], sell_to=[  ], secret=[  ])`**
                - *params*:
                    - consumes all the params of [threefoldtoken.order.sell.update](https://github.com/rivine/recordchain/blob/master/JumpScale9RecordChain/apps/orderbook/schema_crud.toml#L29) object
                    
            - **`update_buy_order(self,comment='', currency_to_buy='', price_max='0.0', amount=0.0, expiration=0, secret='', approved=False, id=0, currency_mine=[  ], buy_from=[  ])`**
                - *params*:
                    - consumes all the params of [threefoldtoken.order.buy.update](https://github.com/rivine/recordchain/blob/master/JumpScale9RecordChain/apps/orderbook/schema_crud.toml#L56) object
                    
            - **`add_sell_order(comment='', currency_to_sell='', price_min='0.0', amount=0.0, expiration=0, approved=False, currency_accept=[  ], sell_to=[  ], secret=[  ])`**
                - *params*:
                    - consumes all the params of [threefoldtoken.order.sell.add](https://github.com/rivine/recordchain/blob/master/JumpScale9RecordChain/apps/orderbook/schema_crud.toml#L16) object
                    
            - **`get_buy_order(order_id=0)`**
                - *params*:
                    - order id
             
            - **`get_sell_order(order_id=0)`**
                - *params*
                    - order id
        
            - **`list_all_buy_orders(sortby='id', desc=False, total_items_in_page=20, page_number=1)`**
                - *params*
                    - sortby: field to sort returned data with. could be any field of [threefoldtoken.order.buy](https://github.com/rivine/recordchain/blob/master/JumpScale9RecordChain/apps/orderbook/schema.toml#L17)
                    - desc: Descending order by default is False, which means data comes in Ascending order
                    - total_items_in_page: Total items in a page, 20 by default
                    - page_number: Page number for pagination
                    
            - **`list_all_sell_orders(sortby='id', desc=False, total_items_in_page, page_number)`**
                - *params*
                    - sortby: field to sort returned data with. could be any field of [threefoldtoken.order.sell](https://github.com/rivine/recordchain/blob/master/JumpScale9RecordChain/apps/orderbook/schema.toml#L1) by default, it's `id`
                    - desc: Descending order by default is False, which means data comes in Ascending order
                    - total_items_in_page: Total items in a page, 20 by default
                    - page_number: Page number for pagination
                    
            - **`list_my_buy_orders(sortby='id', desc=False, total_items_in_page, page_number)`**
                - List/filters only buy orders for the current client only
                - *params*
                    - sortby: field to sort returned data with. could be any field of [threefoldtoken.order.buy](https://github.com/rivine/recordchain/blob/master/JumpScale9RecordChain/apps/orderbook/schema.toml#L17) by default, it's `id`
                    - desc: Descending order by default is False, which means data comes in Ascending order
                    - total_items_in_page: Total items in a page, 20 by default
                    - page_number: Page number for pagination
                   
            - **`list_my_sell_orders(sortby='id', desc=False, total_items_in_page, page_number)`**
                - List/filters only sell orders for the current client only
                - *params*
                    - sortby: field to sort returned data with. could be any field of [threefoldtoken.order.sell](https://github.com/rivine/recordchain/blob/master/JumpScale9RecordChain/apps/orderbook/schema.toml#L1) by default, it's `id`
                    - desc: Descending order by default is False, which means data comes in Ascending order
                    - total_items_in_page: Total items in a page, 20 by default
                    - page_number: Page number for pagination

            - **`remove_buy_order(order_id=0)`**
                - *params*
                    - order id
            - **`remove_sell_order(order_id=0)`**
                - *params*
                    - order id
            - **`list_all_transactions(state='', desc=False)`**
                - List/filter all transactions
                - *params*:
                    - state: empty means all, other choices are [`new`, `pending`, `success`, `failure`]
                    - desc: Descending order by default is False, which means data comes in Ascending order
                    
            - **`list_my_transactions(state='', desc=False)`**       
                 - List/filter transactions that the current client was part of
                - *params*:
                    - state: empty means all, other choices are [`new`, `pending`, `success`, `failure`]
                    - desc: Descending order by default is False, which means data comes in Ascending order


####  General overview on code structure

- **Structure**

    ```
        server
            |
            |__ order_book.py # Exposed CMDs through server & client
            |__ system.py # system CMDs like ping
            
        lib # SAL layer
        
        schema.toml # General schemas
        schema_crud.toml # schemas for crud operations like create/update
    ```
- **Why do We have 2 schema files?**
    - `schema.toml` contains general schemas like `wallet`, `sellorder`, `buyorder`, and `transaction`
    - `schema_crud.toml` contains schemas used in `order_book.py` API which is meant for better code generation forexample:
        - `add_sell_order` we use `threefoldtoken.order.sell.create` from `schema_crud.toml` because it doesn't contain some fields in `threefoldtoken.order.sell` like email address of user
        - `update_sell_order` must contain `id` field that is why we use `threefoldtoken.order.sell.update` 
    - That says ussing multi schema files can be helpful if you want to customize code generation
    for client by hiding or adding certain fields

    - **`WARNING`**
        - Moving data between 2 similar but not identical schemas can be challenging
        that is why we use special technique for this. consider the following example
        ```python
          # obj of type : threefoldtoken.order.buy.create
          obj = j.data.schema.schema_from_url('threefoldtoken.order.buy.create').new()
          
          buy = j.data.schema.schema_from_url('threefoldtoken.order.buy').new()
          buy.copy(obj=obj)
        ```
 
- **Add data to db**
    ```python
      j.servers.gedis.latest.db.tablesp['ordersell'].set(id=id, data=order.data)

        # You can add data to db also using
        # data = j.data.serializer.msgpack.dumps([id, order.data])
        # j.servers.gedis.latest.models.threefoldtoken_order_sell.set(data)

    ```
