from JumpScale9 import j

{# generate the properties #}
{% for cmd in obj.data.cmds %}


def {{cmd.name}}(request, namespace, dbclient):
    {% if cmd.comment != "" %}
    '''
    {{cmd.comment}}
    '''
    {% endif %}
    {% for line in cmd.code.splitlines() %}
    {{line}}
    {% endfor %}

{% endfor %}
