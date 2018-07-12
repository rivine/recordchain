<script type="text/javascript" src="https://cdn.rawgit.com/arahmanhamdy/redisjs/master/build/redisjs.min.js"></script>

<script type="text/javascript">


const SERVER_DOMAIN = '172.17.0.2:8200';
const redisConnection = new RedisConnection(SERVER_DOMAIN);

const successCallback = (redis) => {
Commands = {}
{% for command in commands %}
Commands.{{command.namespace.split('.')[1]}} = {
{% for  name, cmd in command.cmds.items() %}
    "{{name}}": function({{cmd.args_client.strip(",").replace("False", "false").replace("True", "true") if cmd.args_client.strip() != ",schema_out" else ""}} {% if cmd.args_client != "" %},{% endif %}success_callback){
    {% if cmd.schema_in %}
        var args = {}
        {% for prop in cmd.schema_in.properties + cmd.schema_in.lists %}
        {% if prop.js9type.NAME != 'list' %}
        args["{{prop.name}}"] = {{prop.name}}
        {% else %}
        args["{{prop.name}}"] = []
        {{prop.name}}.forEach(function(item){args["{{prop.name}}"].push(item)})
        {% endif %}
        {% endfor %}
        redis["{{command.namespace.split('.')[1]}}.{{name}}"](JSON.stringify(args), (res) => {
            success_callback(res)
        })
    {% else %}
        redis["{{command.namespace.split('.')[1]}}.{{name}}"]((res) => {
            success_callback(res)
        })
    {% endif %}
    },
{% endfor %}
}
{% endfor %}
}

redisConnection.connect(successCallback, function(err){console.log(err)});

</script>