
from js9 import j
import gevent
from gevent import spawn


JSBASE = j.application.jsbase_get_class()

class GedisChatBotFactory(JSBASE):

    def __init__(self):
        JSBASE.__init__(self)
        self.session_greenlets = {}
        j.servers.bot = self

    def session_new(self,sessionid):
        bot = GedisChatBot(sessionid)
        self.session_greenlets[sessionid] = bot  

    def session_work_get(self,sessionid):
        bot = self.session_greenlets[sessionid]
        # print(6)
        # if bot.q_out.empty():
        #     return None
        # print (45678)
        return bot.q_out.get(block=True)
              
    def session_work_set(self,sessionid, val):
        bot = self.session_greenlets[sessionid]
        return bot.q_in.put(val)

    def test(self):
        spawn(test, factory=self)
        gevent.sleep(100)


class GedisChatBot(JSBASE):
    
    def __init__(self,sessionid):
        JSBASE.__init__(self)
        self.sessionid = sessionid
        self.q_out = gevent.queue.Queue() #to browser
        self.q_in = gevent.queue.Queue()  #from browser
        self.greenlet = spawn(mysession, bot=self)


    def string_ask(self,msg):
        print("askstr")
        self.q_out.put(["string_ask",msg])
        return self.q_in.get()

    def int_ask(self,msg):
        print("askint")
        self.q_out.put(["int_ask",msg])
        return self.q_in.get()        

    def md_show(self,msg):
        print(msg)
        self.q_out.put(["md_show",msg])
        self.q_in.get()                

def mysession(bot):
    
    s = bot.string_ask("please fill in")
    i = bot.int_ask("please fill in int")

    if i == 1:
        i+=1

    bot.md_show("#header 1\n\n- %s"%i)


def test(factory):
    sid = "123"
    factory.session_new(sid)
    nr=0
    while True:
        res=factory.session_work_get(sid)
        gevent.sleep(1) #browser is doing something
        nr+=1
        factory.session_work_set(sid,nr)

    
    



