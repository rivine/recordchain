
from js9 import j
import inspect
# import imp

import os

JSBASE = j.application.jsbase_get_class()

class GedisCmd(JSBASE):
    def __init__(self,cmd):
        JSBASE.__init__(self)
        self.cmdobj = cmd
        # self.cmds = cmds
        # self.server = self.cmds.server
        self.name = cmd.name

        if not cmd.schema_in.strip()=="":
            self.schema_in=j.data.schema.schema_from_text(cmd.schema_in)
            self.schema_in.url = self.url+".%s.in"%cmd.name
            self.schema_in.objclass
        else:
            self.schema_in = ""

        if cmd.schema_out.strip()=="":
            cmd.schema_out="res = 0 (I)"

        self.schema_out=j.data.schema.schema_from_text(cmd.schema_out)
        self.schema_out.url = self.url+".%s.out"%self.name
        self.schema_out.objclass     

        self._method = None  

        print(self.code_runtime)

        self.method


    @property
    def url(self):
        return "cmds.%s.%s"%(self.server.instance,self.name)

    @property
    def args(self):
        if self.schema_in=="":
            return ""
        else:
            out= ""
            for prop in  self.schema_in.properties:
                d=prop.default_as_python_code
                if d=="":
                    d = None
                out += "%s=%s, "%(prop.name,d)
            out = out.rstrip().rstrip(",").rstrip()
            return out

    @property
    def code_indent(self):
        return j.data.text.indent(self.cmdobj.code)

    @property
    def comment_indent(self):
        return j.data.text.indent(self.cmdobj.comment)


    @property
    def code_runtime(self):
        code = j.servers.gedis.code_server_template.render(obj=self)
        return code

    @property
    def method(self):
        if self._method is None:
            url = self.url.replace(".","_")
            path = j.servers.gedis.code_generation_dir + "%s.py" % url
            j.sal.fs.writeFile(path,self.code_runtime)
            exec("from %s import %s"% (url,self.name))
            self._method = eval(self.name)
        return self._method