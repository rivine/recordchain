
from js9 import j
import inspect
# import imp
import sys
import os

JSBASE = j.application.jsbase_get_class()


class GedisCmds(JSBASE):

    def __init__(self, server, namespace, class_):
        JSBASE.__init__(self)

        self.server = server

        SCHEMA = """
        @url = jumpscale.gedis.cmd
        @name = GedisCmd
        name = ""
        comment = ""
        code = ""
        schema_in = ""
        schema_out = ""

        @url = jumpscale.gedis.api
        @name = GedisServerSchema
        namespace = ""
        cmds = (LO) !jumpscale.gedis.cmd        
        """
        j.data.schema.schema_add(SCHEMA)
        # s1 = self.schema_from_url("jumpscale.gedis.cmd")
        self.schema = j.data.schema.schema_from_url("jumpscale.gedis.api")

        self.data = self.schema.new()

        self.name = namespace
        self.data.namespace = namespace

        for name, item in inspect.getmembers(class_):
            if name.startswith("_"):
                continue
            if (name, item) in inspect.getmembers(JSBASE):
                continue
            if inspect.isfunction(item):
                cmd = self.data.cmds.new()
                cmd.name = name
                code = inspect.getsource(item)
                cmd.code,cmd.comment,cmd.schema_in, cmd.schema_out= self.source_process(code)
                self.data.cmds.append(cmd)

        code = self.code


    @property
    def code(self):
        code = self.server.code_server_template.render(obj=self)
        return code

    def source_process(self, txt):
        """
        return code, comment, schema_in, schema_out
        """
        txt = j.data.text.strip(txt)
        code = ""
        comment = ""
        schema_in = ""
        schema_out = ""

        state = "START"

        for line in txt.split("\n"):
            lstrip = line.strip()
            if state == "START" and lstrip.startswith("def"):
                state = "DEF"
                continue
            if lstrip.startswith("\"\"\""):
                if state == "DEF":
                    state = "COMMENT"
                    continue
                if state == "COMMENT":
                    state = "CODE"
                    continue
                raise RuntimeError()
            if lstrip.startswith("```") or lstrip.startswith("'''"):
                if state.startswith("SCHEMA"):  # are already in schema go back to comment
                    state = "COMMENT"
                    continue
                if state == "COMMENT":  # are in comment, now found the schema
                    if lstrip.endswith("out"):
                        state = "SCHEMAO"
                    else:
                        state = "SCHEMAI"
                    continue
                raise RuntimeError()
            if state == "SCHEMAI":
                schema_in += "%s\n" % line
                continue
            if state == "SCHEMAO":
                schema_out += "%s\n" % line
                continue
            if state == "COMMENT":
                comment += "%s\n" % line
                continue
            if state == "CODE" or state == "DEF":
                code += "%s\n" % line
                continue
            raise RuntimeError()

        schema_in = j.data.schema.schema_from_text(j.data.text.strip(schema_in))
        schema_out = j.data.schema.schema_from_text(j.data.text.strip(schema_out))

        return j.data.text.strip(code), j.data.text.strip(comment), schema_in, schema_out
