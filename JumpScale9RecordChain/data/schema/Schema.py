
from JumpScale9 import j

JSBASE = j.application.jsbase_get_class()
import os

from .SchemaProperty import SchemaProperty



class Schema(JSBASE):
    def __init__(self, text=None):
        JSBASE.__init__(self)
        self.properties = []
        self.lists = []
        self._template = None
        self._capnp_template = None
        self._obj_class = None
        self.hash = ""
        if text:
            self._schema_from_text(text)

    def _proptype_get(self, txt):

        if "\\n" in txt:
            proptype = j.data.types.multiline
            defvalue = proptype.fromString(txt)

        elif "'" in txt or "\"" in txt:
            proptype = j.data.types.string
            defvalue = proptype.fromString(txt)

        elif "." in txt:
            proptype = j.data.types.float
            defvalue = proptype.fromString(txt)

        elif "true" in txt.lower() or "false" in txt.lower():
            proptype = j.data.types.bool
            defvalue = proptype.fromString(txt)

        elif "[]" in txt:
            proptype = j.data.types.list
            defvalue = []

        elif j.data.types.int.checkString(txt):
            proptype = j.data.types.int
            defvalue = j.data.types.int.fromString(txt)

        else:
            raise RuntimeError("cannot find type for:%s" % txt)

        return (proptype, defvalue)

    def _schema_from_text(self, schema):
        self.logger.debug("load schema:\n%s" % schema)

        self.hash = j.data.hash.blake2_string(schema)

        systemprops = {}
        self.properties = []

        errors = []

        def proptype(prop):
            j.data.types

        def process(line):
            propname, line = line.split("=", 1)
            propname = propname.strip()
            line = line.strip()

            if "!" in line:
                line, pointer_type = line.split("!", 1)
                pointer_type = pointer_type.strip()
                line=line.strip()
            else:
                pointer_type = None

            if "#" in line:
                line, comment = line.split("#", 1)
                line = line.strip()
                comment = comment.strip()
            else:
                comment = ""

            if "(" in line:
                proptype = line.split("(")[1].split(")")[0].strip().lower()
                line = line.split("(")[0].strip()
                proptype = j.data.types.get(proptype)
                defvalue = proptype.fromString(line)
            else:
                proptype, defvalue = self._proptype_get(line)

            if ":" in propname:
                # self.logger.debug("alias:%s"%propname)
                propname, alias = propname.split(":", 1)
            else:
                alias = propname

            return (propname, alias, proptype, defvalue, comment, pointer_type)

        nr = 0
        for line in schema.split("\n"):
            line = line.strip()
            self.logger.debug("L:%s" % line)
            nr += 1
            if line.strip() == "":
                continue
            if line.startswith("@"):
                systemprop_name = line.split("=")[0].strip()[1:]
                systemprop_val = line.split("=")[1].strip()
                systemprops[systemprop_name] = systemprop_val
                continue
            if line.startswith("#"):
                continue
            if "=" not in line:
                errors.append(
                    (nr, "did not find =, need to be there to define field"))
                continue

            propname, alias, proptype, defvalue, comment, pointer_type = process(line)

            p = SchemaProperty()

            p.name = propname
            p.default = defvalue
            p.comment = comment
            p.js9type = proptype
            p.alias = alias
            p.pointer_type = pointer_type

            if p.js9type.NAME is "list":
                self.lists.append(p)
            else:
                self.properties.append(p)

        for key, val in systemprops.items():
            self.__dict__[key] = val

        nr=0
        for s in self.properties:
            s.nr = nr
            self.__dict__["_%s_type" % s.name] = s
            nr+=1

        for s in self.lists:
            s.nr = nr
            self.__dict__["_%s_type" % s.name] = s
            nr+=1

    @property
    def capnp_id(self):
        return self.hash[0:16]

    @property
    def code_template(self):
        if self._template == None:
            self._template = j.data.schema.template_engine.get_template("template_obj.py")
        return self._template

    @property
    def capnp_template(self):
        if self._capnp_template == None:
            self._capnp_template = j.data.schema.template_engine.get_template("schema.capnp")
        return self._capnp_template        

    @property
    def code(self):
        #make sure the defaults render
        for prop in self.properties:
            prop.default_as_python_code
        for prop in self.lists:
            prop.default_as_python_code
        code = self.code_template.render(obj=self)
        # print(code)
        return code

    @property
    def capnp_schema(self):
        code = self.capnp_template.render(obj=self)
        print(code)
        return code


    @property
    def objclass(self):
        if self._obj_class is None:
            path = j.data.schema.code_generation_dir + "dbobj_%s.py" % self.name
            j.sal.fs.writeFile(path,self.code)
            exec("from dbobj_%s import %s"% (self.name, self.name))
            self._obj_class = eval(self.name)
        return self._obj_class

    def get(self,data={}):
        return self.objclass(schema=self,data=data)


    def __str__(self):
        out=""
        for item in self.properties:
            out += str(item) + "\n"
        for item in self.lists:
            out += str(item) + "\n"
        return out

    __repr__=__str__
