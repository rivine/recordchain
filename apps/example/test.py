from js9 import j

print("[-] starting server")

#zerodb 
cl = j.clients.zdb.testdb_server_start_client_get(start=True)  #starts & resets a zdb in seq mode with name test       

app_dir =  j.clients.git.getContentPathFromURLorPath("https://github.com/rivine/recordchain/tree/master/apps/example")
server = j.servers.gedis.configure(host = "localhost", port = "8000", ssl = False, \
    zdb_instance = "test",
    secret = "", app_dir = app_dir, instance='example')

print("[-] server started")

cl = server.client_get()

from IPython import embed;embed(colors='Linux')

print("** DONE **")