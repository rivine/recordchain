@0x{{obj.capnp_id}};

struct Schema {

    {% for prop in obj.properties %}
    {{prop.capnp_schema}}
    {% endfor %}

    {% for prop in obj.lists %}
    {{prop.capnp_schema}}
    {% endfor %}


}