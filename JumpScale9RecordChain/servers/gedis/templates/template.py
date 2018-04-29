from JumpScale9 import j

def {{obj.name}}({{obj.args}}):
    {% if obj.cmdobj.comment != "" %}
    '''
{{obj.comment_indent}}
    '''
    {% endif %}   
{{obj.code_indent}} 
