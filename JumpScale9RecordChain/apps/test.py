from js9 import j
iyoclient = j.clients.itsyouonline.get()                 
jwt = iyoclient.jwt                             
cl = j.clients.gedis2.get('orderbook');                   
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
print("[-] adding sell order2")
s3 = cl.order_book.add_sell_order(price_min='10 XRP', currency_to_sell='BTC' ,currency_accept=['USD'], amount=100, expiration=j.data.time.epoch + 1000, approved=True)

transactions = j.data.serializer.json.loads(cl.order_book.list_all_transactions())

assert transactions[-3]['buy_order_id'] == b1
assert transactions[-3]['sell_order_id'] == s1

assert transactions[-2]['buy_order_id'] == b2
assert transactions[-2]['sell_order_id'] == s2

assert transactions[-1]['buy_order_id'] == b3
assert transactions[-1]['sell_order_id'] == s3

print("** DONE **")

