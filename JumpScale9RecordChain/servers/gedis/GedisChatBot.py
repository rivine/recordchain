
from js9 import j
import gevent
from gevent import spawn
import sys
from importlib import import_module

JSBASE = j.application.jsbase_get_class()

class GedisChatBotFactory(JSBASE):

    def __init__(self,ws):
        JSBASE.__init__(self)
        self.ws = ws
        self.sessions = {}      #open chatsessions
        self.chatflows={}       #are the flows to run, code being executed to talk with user
        self.chatflows_load()
        self.sessions_id_latest=0

    def session_new(self,topic):
        """
        returns the last session id
        """
        self.sessions_id_latest+=1
        topic_method = self.chatflows[topic]
        bot = GedisChatBotSession(self.sessions_id_latest,topic_method)
        self.sessions[self.sessions_id_latest] = bot  
        return self.sessions_id_latest

    def session_work_get(self,sessionid):
        bot = self.sessions[sessionid]
        # print(6)
        # if bot.q_out.empty():
        #     return None
        # print (45678)
        return bot.q_out.get(block=True)
              
    def session_work_set(self,sessionid, val):
        bot = self.sessions[sessionid]
        return bot.q_in.put(val)

    def chatflows_load(self):
        """
        look for the chatflows they are in the appdir underneith dir "chatflows"
        will load them all under self.chatflows
        """
        print("chatflows_load")
        chatflowdir = "%s/chatflows"%self.ws.config.data["app_dir"]
        for chatdir in  j.sal.fs.listFilesInDir(chatflowdir, recursive=True, filter="*.py",followSymlinks=True):
            dpath = j.sal.fs.getDirName(chatdir)
            if dpath not in sys.path:
                sys.path.append(dpath)
            self.logger.info("chat:%s"%chatdir)
            modulename=j.sal.fs.getBaseName(chatdir)[:-3]
            if modulename.startswith("_"):
                continue
            module = import_module(modulename)
            self.chatflows[modulename]=module.chat 

    def test(self):
        spawn(test, factory=self)
        gevent.sleep(100)


class GedisChatBotSession(JSBASE):
    
    def __init__(self,sessionid,topic_method):
        JSBASE.__init__(self)
        self.sessionid = sessionid
        self.q_out = gevent.queue.Queue() #to browser
        self.q_in = gevent.queue.Queue()  #from browser
        self.greenlet = spawn(topic_method, bot=self)


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



def test(factory):
    sid = "123"
    factory.session_new(sid)
    nr=0
    while True:
        res=factory.session_work_get(sid)
        gevent.sleep(1) #browser is doing something
        nr+=1
        factory.session_work_set(sid,nr)

    
    



