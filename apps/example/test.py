from js9 import j
print("[-] starting server")

#TODO, can we autoconfigure client & server, is all for test anyhow

#zerodb 
cl = j.clients.zdb.testdb_server_start_client_get(start=start)  #starts & resets a zdb in seq mode with name test       
# db = j.data.bcdb.get(cl)

server = j.servers.gedis.configure(host = "localhost", port = "8000", websockets_port = "8001", ssl = False, \
    zdb_instance = "test",
    secret = "", apps_dir = "", instance='orderbook')
server.start()
print("[-] server started")

cl = server.client_get()

from IPython import embed;embed(colors='Linux')

print("** DONE **")

