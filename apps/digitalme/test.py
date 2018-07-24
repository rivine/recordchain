from js9 import j
print("[-] starting server")

name = "{{name}}"

dir = "{{DIRS.TMPDIR}}"

#TODO, can we autoconfigure client & server, is all for test anyhow

server = j.servers.gedis.configure(host = "localhost", port = "8000", websockets_port = "8001", ssl = False, secret = "", apps_dir = "", instance='orderbook')
server.start()
print("[-] server started")

iyoclient = j.clients.itsyouonline.get()                 
jwt = iyoclient.jwt                             
cl = j.clients.gedis.configure(host="localhost", port="8000", instance="orderbook", ssl=False, secret="" )
cl.order_book.login(jwt=jwt, addr='addr', ipaddr='8.8.8.8')


print("** DONE **")

