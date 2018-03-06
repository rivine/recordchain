class {{name}}():
    
    def __init__(self,schema,data={}):
        self.schema = schema

        for key,val in data.items():
            self.__dict__[key] = val

{{#properties}}
    @property
    def {{alias}}(self):
        '''
        {{comment}}
        '''
        return self._{{alias}}
        
    @{{alias}}.setter
    def {{alias}}(self,val):
        self._{{alias}} = val

{{/properties}}