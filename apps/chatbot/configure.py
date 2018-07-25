from js9 import j

print("[-] zerodb started / configured")
#zerodb 
cl = j.clients.zdb.testdb_server_start_client_get(start=True)  #starts & resets a zdb in seq mode with name test       

server = j.servers.gedis.configure(host = "localhost", port = "8000", websockets_port = "8001", ssl = False, \
    zdb_instance = "test",
    secret = "", app_dir = "", instance='example')
# server.start()
print("[-] server configured")

# cl = server.client_get()

print("** DONE **")