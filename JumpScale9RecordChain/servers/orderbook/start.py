
from js9 import j

reset = False
serverinstance = "orderbook"
server=j.servers.gedis2.get(serverinstance)

#create backend database, use same admin secret as the server 
j.data.bcdb.db_start("orderbook",adminsecret=server.config.data["adminsecret_"],reset=reset)
db=j.data.bcdb.get("orderbook")

db.tables_get() #will get it from current path
server.db = db
#tables are now in db.tables as dict

server.generate(reset=True)

server.init()

server.start()
