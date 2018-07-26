// SERVER_DOMAIN & SERVER_PORT will come from the client.js 
const client = (function(){
    var socket = new WebSocket("wss://%%host%%/");
    var connected = false
    var connect = ()=> {
        return new Promise(res =>{
            if(!connected){
                socket.onopen = () => {
                connected = true
                res(true)
            }
            } else {
                res(true)
            }
        })
      }
      var execute = (command, args) => {
          return connect().then((res) => { return new Promise((resolve, fail) => {
              socket.onmessage = function(e) {
                  resolve(e.data)
              }
              if (args.length != 0){
                  socket.send(command + " " + args)
              } else {
                  socket.send(command)
              }
          })})
      }
    
    var client = {}
    
    
    client.system = {
    
        "api_meta": async () => {
        
            return await execute("system.api_meta", "")
        
        },
    
        "core_schemas_get": async () => {
        
            return await execute("system.core_schemas_get", "")
        
        },
    
        "get_web_client": async () => {
        
            return await execute("system.get_web_client", "")
        
        },
    
        "ping": async () => {
        
            return await execute("system.ping", "")
        
        },
    
        "ping_bool": async () => {
        
            return await execute("system.ping_bool", "")
        
        },
    
        "schema_urls": async () => {
        
            return await execute("system.schema_urls", "")
        
        },
    
        "test": async (name='', nr=0) => {
        
            var args = {}
            
            
            args["name"] = name
            
            
            
            args["nr"] = nr
            
            
            return await execute("system.test", JSON.stringify(args))
        
        },
    
        "test_nontyped": async (name,nr) => {
        
            return await execute("system.test_nontyped", "")
        
        },
    
    }
    
    client.myapp = {
    
        "test_dns": async (id=0,type='', val='') => {
        
            var args = {}
            
            
            args["type"] = type
            
            
            
            args["val"] = val
            
            
            return await execute("myapp.test_dns", JSON.stringify(args))
        
        },
    
        "test_dns2": async (type,val) => {
        
            return await execute("myapp.test_dns2", "")
        
        },
    
    }
    
return client    
})()
export {
    client as default
} 