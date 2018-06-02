


from js9 import j

# JSBASE = j.application.jsbase_get_class()

class CMDS():
    
    def __init__(self,client,cmds):
        # JSBASE.__init__(self)   
        self._client = client
        self._redis = client.redis   
        self._cmds = cmds
        self._name = "{{obj.cmds_name_lower}}"

    {# generate the actions #}
    {% for name,cmd in obj.cmds.items() %}


    def {{name}}(self{{cmd.args_client}}):
        {% if cmd.comment != "" %}
        '''
{{cmd.comment_indent2}}
        '''
        {% endif %}

        {% if cmd.schema_in != None %}
        #schema in exists
        schema_in = self._cmds["{{name}}"].schema_in
        args = schema_in.new()
        {% for prop in cmd.schema_in.properties %}
        args.{{prop.name}} = {{prop.name}}
        {% endfor %}

        res = self._redis.execute_command("{{obj.cmds_name_lower}}.{{name}}",args.data)

        {% else %}  
        return self._redis.execute_command("{{obj.cmds_name_lower}}.{{name}}")
        {% endif %}        
        
        {% if cmd.schema_out != None %}
        schema_out = self._cmds["{{name}}"].schema_out
        obj = schema_out.get(capnpbin=res)
        {% endif %}        

        return obj


    {% endfor %}

