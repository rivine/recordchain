
from js9 import j
import inspect
import imp

import os

JSBASE = j.application.jsbase_get_class()

class GedisCmd(JSBASE):
    def __init__(self,cmds,cmd):
        JSBASE.__init__(self)

        self.cmdobj = cmd
        self.data = cmd.data
        self.cmds = cmds
        self.server = self.cmds.server
        self.name = cmd.name

        if not cmd.schema_in.strip()=="":
            self.schema_in=j.data.schema.schema_from_text(cmd.schema_in,url=self.namespace+".%s.in"%cmd.name)
            self.schema_in.objclass
        else:
            self.schema_in = None

        if cmd.schema_out:
            self.schema_out = j.data.schema.schema_from_text(cmd.schema_out,url=self.namespace+".%s.out"%cmd.name)
            self.schema_out.objclass     
        else:
            self.schema_out = None

        self._method = None 

        print(self.code_runtime)

        self.method



    @property
    def namespace(self):
        return self.cmds.data.namespace

    @property
    def args(self):
        if self.schema_in==None:
            return self.cmdobj.args
        else:
            out= ""
            for prop in  self.schema_in.properties:
                d=prop.default_as_python_code
                if d=="":
                    d = None
                out += "%s=%s, "%(prop.name,d)            
            out = out.rstrip().rstrip(",").rstrip()
            out += ",schema_out=None"
            return out

    @property
    def code_indent(self):
        return j.data.text.indent(self.cmdobj.code)

    @property
    def comment_indent(self):
        return j.data.text.indent(self.cmdobj.comment)


    @property
    def code_runtime(self):
        code = j.servers.gedis2.code_server_template.render(obj=self)
        return code

    @property
    def method(self):
        if self._method is None:
            path = j.servers.gedis2.code_generation_dir + "%s_%s.py" % (self.namespace,self.name)
            j.sal.fs.writeFile(path,self.code_runtime)
            m=imp.load_source(name=self.namespace+"."+self.name, pathname=path)
            self._method = m.action
        return self._method