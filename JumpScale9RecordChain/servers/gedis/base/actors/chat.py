from js9 import j


JSBASE = j.application.jsbase_get_class()

class chat(JSBASE):
    """
    """
    def __init__(self):
        JSBASE.__init__(self)


    def work_get(self, sessionid,schema_out):
        """
        ```in
        sessionid = "" (S)
        ```
        ```out
        cat = "" (S)
        msg = "" (S)
        ```

        """
        cat,msg = j.servers.bot.session_work_get(sessionid)
        return {"cat":cat,"msg":msg}

    def work_report(self, sessionid, result,schema_out):
        """
        ```in
        sessionid = "" (S)
        result = "" (S)
        ```

        ```out
        ```

        """
        j.servers.bot.session_work_set(sessionid,result)

    def session_alive(self,sessionid,schema_out):
        #TODO:*1 check if greenlet is alive
        pass
        

