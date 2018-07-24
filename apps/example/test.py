from js9 import j

#TODO, can we autoconfigure client & server, is all for test anyhow

server = j.servers.gedis.configure(host = "{{config.host}}", port = {{config.port}}, \
    websockets_port = {{config.websockets_port}}, ssl = "{{config.ssl}}", secret = "{{config.secret}}", \
    apps_dir = "{{config.apps_dir}}", instance='{{instance}}',configureclient=True)


print("[-] starting server")
server.start()
print("[-] server started")

iyoclient = j.clients.itsyouonline.get()                 
jwt = iyoclient.jwt                             
cl = j.clients.gedis.get(instance="{{instance}}")
cl.order_book.login(jwt=jwt, addr='addr', ipaddr='8.8.8.8')


print("** DONE **")

