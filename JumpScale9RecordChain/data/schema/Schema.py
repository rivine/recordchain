import imp

from JumpScale9 import j
from .SchemaProperty import SchemaProperty

JSBASE = j.application.jsbase_get_class()


class Schema(JSBASE):

    def __init__(self, text=None, url=""):
        JSBASE.__init__(self)
        self.properties = []
        self.lists = []
        self._template = None
        self._capnp_template = None
        self._obj_class = None
        self._capnp = None
        self.hash = ""
        self._index_list = None
        self._SCHEMA = True
        if url:
            self.url = url
        else:
            self.url = ""

        self.name = ""
        if text:
            self._schema_from_text(text)

    def _proptype_get(self, txt):

        if "\\n" in txt:
            js9type = j.data.types.multiline
            defvalue = js9type.fromString(txt)

        elif "'" in txt or "\"" in txt:
            js9type = j.data.types.string
            defvalue = js9type.fromString(txt)

        elif "." in txt:
            js9type = j.data.types.float
            defvalue = js9type.fromString(txt)

        elif "true" in txt.lower() or "false" in txt.lower():
            js9type = j.data.types.bool
            defvalue = js9type.fromString(txt)

        elif "[]" in txt:
            js9type = j.data.types._list()
            js9type.SUBTYPE = j.data.types.string
            defvalue = []

        elif j.data.types.int.checkString(txt):
            js9type = j.data.types.int
            defvalue = js9type.fromString(txt)

        else:
            raise RuntimeError("cannot find type for:%s" % txt)

        return (js9type, defvalue)

    def _schema_from_text(self, schema):
        self.logger.debug("load schema:\n%s" % schema)

        self.text = schema

        self.hash = j.data.hash.blake2_string(schema)

        systemprops = {}
        self.properties = []

        errors = []

        def process(line):
            propname, line = line.split("=", 1)
            propname = propname.strip()
            line = line.strip()

            if "!" in line:
                line, pointer_type = line.split("!", 1)
                pointer_type = pointer_type.strip()
                line = line.strip()
            else:
                pointer_type = None

            if "#" in line:
                line, comment = line.split("#", 1)
                line = line.strip()
                comment = comment.strip()
            else:
                comment = ""

            if "(" in line:
                line_proptype = line.split("(")[1].split(")")[0].strip().lower()
                line_wo_proptype = line.split("(")[0].strip()
                if line_proptype == "o":  # special case where we have subject directly attached
                    js9type = j.data.types.get("jo")
                    js9type.SUBTYPE = pointer_type
                    defvalue = ""
                else:
                    js9type = j.data.types.get(line_proptype)
                    defvalue = js9type.fromString(line_wo_proptype)
            else:
                js9type, defvalue = self._proptype_get(line)

            if ":" in propname:
                # self.logger.debug("alias:%s"%propname)
                propname, alias = propname.split(":", 1)
            else:
                alias = propname

            if alias[-1] == "*":
                alias = alias[:-1]

            if propname in ["id"]:
                raise RuntimeError("do not use 'id' in your schema, is reserved for system.")

            return (propname, alias, js9type, defvalue, comment, pointer_type)

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
                systemprops[systemprop_name] = systemprop_val.strip("\"").strip("'")
                continue
            if line.startswith("#"):
                continue
            if "=" not in line:
                errors.append(
                    (nr, "did not find =, need to be there to define field"))
                continue

            propname, alias, js9type, defvalue, comment, pointer_type = process(line)

            p = SchemaProperty()

            if propname.endswith("*"):
                propname = propname[:-1]
                p.index = True

            p.name = propname
            p.default = defvalue
            p.comment = comment
            p.js9type = js9type
            p.alias = alias
            p.pointer_type = pointer_type

            if p.js9type.NAME is "list":
                self.lists.append(p)
            else:
                self.properties.append(p)

        for key, val in systemprops.items():
            self.__dict__[key] = val

        nr = 0
        for s in self.properties:
            s.nr = nr
            self.__dict__["property_%s" % s.name] = s
            nr += 1

        for s in self.lists:
            s.nr = nr
            self.__dict__["property_%s" % s.name] = s
            nr += 1

    @property
    def capnp_id(self):
        if self.hash == "":
            raise RuntimeError("hash cannot be empty")
        return "f" + self.hash[1:16]  # first bit needs to be 1

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
        # make sure the defaults render
        for prop in self.properties:
            prop.default_as_python_code
        for prop in self.lists:
            prop.default_as_python_code
        code = self.code_template.render(obj=self)
        return code

    @property
    def capnp_schema(self):
        code = self.capnp_template.render(obj=self)
        return code

    @property
    def capnp(self):
        if not self._capnp:
            self._capnp = j.data.capnp3.getSchemaFromText(self.capnp_schema)
        return self._capnp

    @property
    def objclass(self):
        if self._obj_class is None:
            url = self.url.replace(".", "_")
            path = j.sal.fs.joinPaths(j.data.schema.code_generation_dir, "%s.py" % url)
            j.sal.fs.writeFile(path, self.code)
            m = imp.load_source(name="url", pathname=path)
            self._obj_class = m.ModelOBJ
        return self._obj_class

    def get(self, data={}, capnpbin=None):
        return self.objclass(schema=self, data=data, capnpbin=capnpbin)

    def new(self):
        return self.get()

    @property
    def index_list(self):
        if self._index_list == None:
            self._index_list = []
            for prop in self.properties:
                if prop.index:
                    self._index_list.append(prop.alias)
        return self._index_list

    def __str__(self):
        out = ""
        for item in self.properties:
            out += str(item) + "\n"
        for item in self.lists:
            out += str(item) + "\n"
        return out

    __repr__ = __str__
