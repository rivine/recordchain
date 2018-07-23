// SERVER_DOMAIN & SERVER_PORT will come from the client.js 
var socket = new WebSocket("ws://%%host%%/");
var execute = (command, args) => {
    return new Promise((resolve, fail) => {
        socket.onmessage = function(e) {
            resolve(e.data)
        }
        if (args.length != 0){
            socket.send(command + " " + args)
        } else {
            socket.send(command)
        }
    });
}

var client = {}

{% for command in commands %}
client.{{command.namespace.split('.')[1]}} = {
{% for  name, cmd in command.cmds.items() %}
    "{{name}}": async ({{cmd.args_client.strip(",").replace("False", "false").replace("True", "true") if cmd.args_client.strip() != ",schema_out" else ""}}) => {
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
        return await execute("{{command.namespace.split('.')[1]}}.{{name}}", JSON.stringify(args))
    {% else %}
        return await execute("{{command.namespace.split('.')[1]}}.{{name}}", "")
    {% endif %}
    },
{% endfor %}
}
{% endfor %}


