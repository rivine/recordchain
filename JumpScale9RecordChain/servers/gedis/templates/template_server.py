from JumpScale9 import j

{# generate the properties #}
{% for cmd in obj.data.cmds %}

def {{cmd.name}}():
    {% if prop.comment != "" %}
    '''
    {{prop.comment}}
    '''
    {% endif %}

{% endfor %}
