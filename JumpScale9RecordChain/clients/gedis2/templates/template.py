


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
        {% if prop.js9type.NAME == 'numeric' %}
        args.{{prop.name}} = j.data.types.numeric.clean({{prop.name}})
        {% else %}
        args.{{prop.name}} = {{prop.name}}
        {% endif %}
        {% endfor %}


        {% for prop in cmd.schema_in.lists %}
        for item in {{prop.name}}:
            args.{{prop.name}}.append(item)
        {% endfor %}

        res = self._redis.execute_command("{{obj.cmds_name_lower}}.{{name}}",j.data.serializer.msgpack.dumps([id if not callable(id) else None, args.data]))

        {% else %}
        {% set args = cmd.cmdobj.args.split(',') if cmd.cmdobj.args else [] %}

        {% if args|length == 0 %}
        res =  self._redis.execute_command("{{obj.cmds_name_lower}}.{{name}}")
        {% else %}
        # send multi args with no prior knowledge of schema
        res = self._redis.execute_command("{{obj.cmds_name_lower}}.{{name}}", {{ cmd.args_client.lstrip(',')}})
        {% endif %}
        {% endif %}
        {% if cmd.schema_out != None %}
        schema_out = self._cmds["{{name}}"].schema_out
        res = schema_out.get(capnpbin=res)
        {% else %}
        {% endif %}
        
        if isinstance(res, bytes):
            return j.data.serializer.json.loads(res.decode())
        return res


    {% endfor %}

