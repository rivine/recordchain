from JumpScale9 import j

List0=j.data.schema.list_base_class_get()

class {{obj.name}}():
    
    def __init__(self,schema,data={}, capnpbin=None):
        self.schema = schema
        self.capnp = schema.capnp

        self.changed_list = False
        self.changed_prop = False

        if capnpbin != None:
            self._cobj = self.capnp.from_bytes(capnpbin)
        else:
            self._cobj = self.capnp.new_message()

            for key,val in data.items():
                self.__dict__[key] = val

        {# list not as property#}
        {% for ll in obj.lists %}    
        self.{{ll.alias}} = List0(self,self._cobj.{{ll.name_camel}}, self.schema.property_{{ll.name}})
        {% endfor %}


    {# generate the properties #}
    {% for prop in obj.properties %}
    @property 
    def {{prop.alias}}(self):
        {% if prop.comment != "" %}
        '''
        {{prop.comment}}
        '''
        {% endif %}
        return self._cobj.{{prop.name_camel}}
        
    @{{prop.alias}}.setter
    def {{prop.alias}}(self,val):
        #will make sure that the input args are put in right format
        val = {{prop.js9_typelocation}}.clean(val)
        self._cobj.{{prop.name_camel}} = val
        self.changed_prop = True

    {% if prop.js9type.NAME == "numeric" %}
    @property 
    def {{prop.alias}}_usd(self):
        return {{prop.js9_typelocation}}.bytes2cur(self.{{prop.alias}})
    @property 
    def {{prop.alias}}_eur(self):
        return {{prop.js9_typelocation}}.bytes2cur(self.{{prop.alias}},curcode="eur")

    def {{prop.alias}}_cur(self,curcode):
        """
        @PARAM curcode e.g. usd, eur, egp, ...
        """
        return {{prop.js9_typelocation}}.bytes2cur(self.{{prop.alias}},curcode=curcode)

    {% endif %}

    {% endfor %}

    def check(self):
        #checks are done while creating ddict, so can reuse that
        self.ddict
        return True

    @property
    def cobj(self):
        if self.changed_list:            
            ddict = self._cobj.to_dict()
            print("cobj")
            {% for prop in obj.lists %}
            if self.{{prop.alias}}._copied:
                #means the list was modified
                if "{{prop.name_camel}}" in ddict:
                    ddict.pop("{{prop.name_camel}}")
                ddict["{{prop.name_camel}}"]=[]
                for item in self.{{prop.name}}._inner_list:
                    ddict["{{prop.name_camel}}"].append(item)                
            {% endfor %}
            try:
                self._cobj = self.capnp.new_message(**ddict)
            except Exception as e:
                msg="\nERROR: could not create capnp message\n"
                msg+=j.data.text.indent(j.data.serializer.json.dumps(ddict,sort_keys=True,indent=True),4)+"\n"
                msg+="schema:\n"
                msg+=j.data.text.indent(str(self.schema.capnp_schema),4)+"\n"
                msg+="error was:\n%s\n"%e
                raise RuntimeError(msg)
        return self._cobj

    def changed_reset(self):
        self.changed_list = False
        self.changed_prop = False
        {% for prop in obj.lists %}
        if self.{{prop.name}}._copied:
            #means the list was modified
            self.{{prop.name}}._inner_list = []
            self.{{prop.name}}._copied = False                     
        {% endfor %}
        
        
    @property
    def ddict(self):
        d={}
        {% for prop in obj.properties %}
        d["{{prop.name}}"] = self._cobj.{{prop.name_camel}}
        {% endfor %}
        {% for prop in obj.lists %}
        #check if the list has the right type
        d["{{prop.name}}"] = self.{{prop.name}}.pylist
        {% endfor %}
        return d

    @property
    def ddict_hr(self):
        """
        human readable dict
        """
        d={}
        {% for prop in obj.properties %}
        d["{{prop.name}}"] = {{prop.js9_typelocation}}.toHR(self._cobj.{{prop.name_camel}})
        {% endfor %}
        {% for prop in obj.lists %}
        #check if the list has the right type
        d["{{prop.name}}"] = self.{{prop.name}}.pylist
        {% endfor %}
        return d

    @property
    def json(self):
        return j.data.serializer.json.dumps(self.ddict)

    @property
    def msgpack(self):
        return j.data.serializer.msgpack.dumps(self.ddict)

    def __str__(self):
        return j.data.serializer.json.dumps(self.ddict_hr,sort_keys=True, indent=True)

    __repr__ = __str__