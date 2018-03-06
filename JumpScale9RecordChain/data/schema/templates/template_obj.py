from JumpScale9 import j

class {{obj.name}}():
    
    def __init__(self,schema,data={}):
        self.schema = schema

        {# list not as property#}
        {% for ll in obj.lists %}    
        self.{{ll.alias}} = [] #{{ll.comment}}
        {% endfor %}

        {% for prop in obj.properties %}    
        self._{{prop.alias}} = {{prop.default_as_python_code}}
        {% endfor %}

        for key,val in data.items():
            self.__dict__[key] = val


    {# generate the properties #}
    {% for prop in obj.properties %}
    @property 
    def {{prop.alias}}(self):
        {% if prop.comment != "" %}
        '''
        {{prop.comment}}
        '''
        {% endif %}
        return self._{{prop.alias}}
        
    @{{prop.alias}}.setter
    def {{prop.alias}}(self,val):
        #will make sure that the input args are put in right format
        val = {{prop.js9_typelocation}}.clean(val)
        self._{{prop.alias}} = val

    {% if prop.js9type.NAME == "numeric" %}
    @property 
    def {{prop.alias}}_usd(self):
        return j.tools.numtools.text2val(self.{{prop.alias}})
    {% endif %}

    {% endfor %}

    def check(self):
        #checks are done while creating ddict, so can reuse that
        self.ddict
        return True

    @property
    def ddict(self):
        d={}
        {% for prop in obj.properties %}
        d["{{prop.name}}"] = self.{{prop.alias}}
        {% endfor %}
        {% for prop in obj.lists %}
        #check if the list has the right type
        for x in len(self.{{prop.alias}}):
            self.schema._{{prop.name}}_type.SUBTYPE.clean(item) #check that each item of the list is following good type
        d["{{prop.name}}"] = self.{{prop.alias}}
        {% endfor %}
        return d

    @property
    def json(self):
        return j.data.serializer.json.dumps(self.ddict)

    @property
    def msgpack(self):
        return j.data.serializer.msgpack.dumps(self.ddict)

    def __str__(self):
        return j.data.serializer.json.dumps(self.ddict,sort_keys=True, indent=True)

    __repr__ = __str__