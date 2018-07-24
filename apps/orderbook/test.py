from js9 import j
print("[-] starting server")

#TODO, can we autoconfigure client & server, is all for test anyhow

server = j.servers.gedis.configure(host = "localhost", port = "8000", websockets_port = "8001", ssl = False, secret = "", app_dir = "", instance='orderbook')
server.start()
print("[-] server started")

iyoclient = j.clients.itsyouonline.get()                 
jwt = iyoclient.jwt                             
cl = j.clients.gedis.configure(host="localhost", port="8000", instance="orderbook", ssl=False, secret="" )
cl.order_book.login(jwt=jwt, addr='addr', ipaddr='8.8.8.8')

print("[-] adding buy order1")
b1 = cl.order_book.add_buy_order(price_max='10 ETH', currency_to_buy='BTC', currency_mine=['USD'], amount=100, expiration=j.data.time.epoch + 1000, approved=True)
print("[-] adding buy order2")
b2 = cl.order_book.add_buy_order(price_max='10 ETH', currency_to_buy='BTC', currency_mine=['USD'], amount=100, expiration=j.data.time.epoch + 1000, approved=True)
print("[-] adding buy order3")
b3 = cl.order_book.add_buy_order(price_max='10 ETH', currency_to_buy='BTC', currency_mine=['USD'], amount=100, expiration=j.data.time.epoch + 1000, approved=True)
print("[-] adding sell order1")
s1 = cl.order_book.add_sell_order(price_min='10 XRP', currency_to_sell='BTC' ,currency_accept=['USD'], amount=100, expiration=j.data.time.epoch + 1000, approved=True)
print("[-] adding sell order2")
s2 = cl.order_book.add_sell_order(price_min='10 XRP', currency_to_sell='BTC' ,currency_accept=['USD'], amount=100, expiration=j.data.time.epoch + 1000, approved=True)
print("[-] adding sell order3")
s3 = cl.order_book.add_sell_order(price_min='10 XRP', currency_to_sell='BTC' ,currency_accept=['USD'], amount=100, expiration=j.data.time.epoch + 1000, approved=True)

transactions = cl.order_book.list_all_transactions()
transactions = transactions.transactions

print("[-] validating transactions")
transaction = transactions.pop()
assert transaction.buy_order_id == b3
assert transaction.sell_order_id == s3
transaction = transactions.pop()
assert transaction.buy_order_id == b2
assert transaction.sell_order_id == s2
transaction = transactions.pop()
assert transaction.buy_order_id == b1
assert transaction.sell_order_id == s1

print("** DONE **")

