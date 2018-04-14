
from js9 import j
import inspect
import imp

SCHEMA = """
@url = jumpscale.gedis.cmd
@name = GedisCmd
name = ""
comment = ""
schema = ""

@url = jumpscale.gedis.serverschema
@name = GedisServerSchema
cmds = "" (LO) !jumpscale.gedis.cmd
"""



JSBASE = j.application.jsbase_get_class()

class GedisCmds(JSBASE):
    def __init__(self):
        JSBASE.__init__(self)

        self.cmds = {}