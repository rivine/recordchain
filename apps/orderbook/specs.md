# OrderBook

## Description
- An order book is a ledger containing all pending orders [buy/sell]
- these orders are paired up as soon as their requirements are fulfilled.
- A transaction is issued with each match
- When adding/editing an order, if `approved` field is set to True
no further updates or deletes to this order is possible, and order is
scheduled for matching
- Upon matching, list of possible transactions are created and needed to be executed
- upon failure of transactions, orders eligible for transactions are updated by the result of these transactions

## Needed APIs
- Orders
    - Add
    - update
    - delete
    - list/filter (all/client) orders
    
- Matching
- Trading
- Transactions
    - list/filter (all/client) transactions with tht ability to filter (all/pending/successed/failed) ones

## Goal
- implement an orderbook server(on top of gedis server)
- Orders are saved in memory and committed to db for history only

## Deliverables
- Order book server using gedis with SSL support
- Python client for orderbook
- Create a matcher to match selling with buying orders
- Create a trader to actually do the transactions to user wallets

## Design
- API layer accessible through gedis server
- SAL layer for handling logic (called by API)
- Matcher
- Trader

# Flow

- Client logs in using `JWT` from [It's you online](https://itsyou.online) and wallet info
- Then client can do CRUD opertations on orders
- If client added/updated an order with the field `approved` set to `True` this means order is
no more eligible for further updates and it became eligible to be matched against other
approved orders
- **Matcher** 
    - There's a `Matcher` daemon waiting for approved orders and for each added `approved` order
     it will start matching that order immediately
     
    - Matcher notifies `Trader` then  with a list of possible matches
- **Trader**
    - There's a `Trader` daemon running and waiting to be notified with a list of possible
    transactions
    - For each transaction in these transactions:
        - persisit transaction to DB with state of `pending`
        - Try execute transaction and if failed, update original order back with original amounts of money
   

# Matching algorithm

we are implementing price-time-priority/fifo algorithm to match orders which means that orders with better prices will be matched first, In case that there are multible orders with the same price the order coming first will be matched first.

## How matcher works

- First we sort orders, buy orders are sorted descending by price_max and ascending by id, then sell orders are sorted ascending by price_min.
- Then we check each buy order againest all sell orders to find the best match, accourding to the following:
    - make sure that orders are not expired by checking the expiry date againest the current time
    - check if sell order or buy order has secrets and if so make sure that these secrets match
    - check if orders have the same targeted currencies for instance I'm trying to sell the same currency you want to buy and I accept one of your own currencies as price.
    - check if the price_min for sell is less than the price_max for buy
    - if all the previous checks passed, there is a possible match so we compare the sell order with the previous best sell order, if there is no previous sell orders, the current order will be considered the best sell order until we find a better sell order
    
- When a best match found we calculate the trade amount and generate a transaction
- Transactions are sent to the trader to do the actual exchange and update database for successful and unsuccessful exchanges


## Code
[Order book](https://github.com/rivine/recordchain/tree/master/JumpScale9RecordChain/servers/orderbook)

