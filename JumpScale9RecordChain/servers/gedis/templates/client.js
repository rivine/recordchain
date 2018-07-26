// SERVER_DOMAIN & SERVER_PORT will come from the client.js 
const client = (function(){
    var connect = () => {
        return new Promise(function (resolve, reject) {
            var socket = new WebSocket("wss://%%host%%/");
            socket.onopen = function () {
                resolve(socket);
            };
            socket.onerror = function (err) {
                reject(err);
            };
        });
    }
    var execute = (command, args) => {
        return connect().then((socket, err) => {
            return new Promise((resolve, fail) => {
                if (socket) {
                    socket.onmessage = function (e) {
                        resolve(e.data)
                        socket.close()
                    }
                    if (args.length != 0) {
                        socket.send(command + " " + args)
                    } else {
                        socket.send(command)
                    }
                } else {
                    fail(err)
                }

            })
        })
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
return client    
})()
export {
    client as default
} 