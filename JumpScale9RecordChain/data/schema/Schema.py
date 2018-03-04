
from JumpScale9 import j

JSBASE = j.application.jsbase_get_class()

from .SchemaProperty import SchemaProperty


class Schema(JSBASE):
    def __init__(self):
        JSBASE.__init__(self)

    def schema_from_text(self, schema):
        systemprops = {}

        errors = []

        def proptype(prop):
            

        def process(line):
            propname, line = line.split("=", 1)
            propname = propname.strip()
            line = line.strip()

            if "#" in line:
                line, comment = line.split("#", 1)
                line = line.strip()
                comment = comment.strip()

            if "(" in line:
                proptype = line.split("(")[1].split(")")[0].strip().lower()
                line = line.split("(")[0].strip()

            if '"' in post:
                #string or Numeric

        nr = 0
        for line in schema.split("\n"):
            nr += 1
            if line.strip() == "":
                continue
            if line.startswith("@"):
                systemprop_name = line.split("=")[0].strip()[1:]
                systemprop_val = line.split("=")[1].strip()
                systemprops[systemprop_name] = systemprop_val
                continue
            if line..startswith("#"):
                continue
            if "=" not in line:
                errors.append((nr, "did not find =, need to be there to define field"))
                continue
            process(line)
            

    def test(self):
        schema = """
        @name = test
        nr = 0
        date_start = 0 (D)
        description = ""
        token_price = " USD"
        cost_estimate:hw_cost = 0.0
        U = 0.0
        pool_type = "managed,unmanaged" (E)
        """
