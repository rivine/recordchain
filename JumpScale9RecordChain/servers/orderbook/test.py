from js9 import j
import os

def start(reset=True):
    if reset:
        #FOR CURRENT TEST TO MAKE SURE WE START FROM NOTHING
        j.sal.fs.remove("%s/codegen/"%j.dirs.VARDIR)
        bcdb=j.data.bcdb.get("test")  #has been set on start.py, will delete it here
        bcdb.destroy()
        j.tools.tmux.killall()

    lpath = j.sal.fs.getDirName(os.path.abspath(__file__)) 
    cmd = "cd %s;python3 start.py"%lpath
    j.tools.tmux.execute(cmd, session='main', window='orderbook',pane='main', session_reset=False, window_reset=True)
    res = j.sal.nettools.waitConnectionTest("localhost",6000)

start(True)

r = j.servers.gedis2.client_get("orderbook")
ping1value = r._client.redis.execute_command("system.ping")
assert ping1value == b'PONG'

#o = r.models.threefoldtoken_order_buy.new()
#TODO:*1 TEST MORE, above crashes, something wrong with numeric

#should do a test where we create orders, do an exchange ...

from IPython import embed;embed(colors='Linux')