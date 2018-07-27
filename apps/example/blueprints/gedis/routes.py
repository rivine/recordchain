from flask import render_template, redirect, request, url_for
from blueprints.gedis import *
from js9 import j

login_manager = j.servers.web.latest.loader.login_manager

@blueprint.route('/')
def route_default():
    return redirect('/%s/index_.html'%name)


# @login_required
@blueprint.route('/<template>')
def route_template(template):
    return render_template(template)



#         if self.ssl:
#             self.ssl_priv_key_path, self.ssl_cert_path = self.sslkeys_generate()

#             # Server always supports SSL
#             # client can use to talk to it in SSL or not
#             self.redis_server = StreamServer(
#                 (self.host, self.port),
#                 spawn=Pool(),
#                 handle=RedisRequestHandler(self.instance, self.cmds, self.classes, self.cmds_meta).handle,
#                 keyfile=self.ssl_priv_key_path,
#                 certfile=self.ssl_cert_path
#             )
#             self.websocket_server = pywsgi.WSGIServer(('0.0.0.0', self.websockets_port), self.websocketapp, handler_class=WebSocketHandler)
#         else:
#             self.redis_server = StreamServer(
#                 (self.host, self.port),
#                 spawn=Pool(),
#                 handle=RedisRequestHandler(self.instance, self.cmds, self.classes, self.cmds_meta).handle
#             )
#             self.websocket_server = pywsgi.WSGIServer(('0.0.0.0', self.websockets_port), self.websocketapp, handler_class=WebSocketHandler)




#     def websocketapp(self, environ, start_response):
#         if '/static/' in environ['PATH_INFO']:
#             items = [p for p in environ['PATH_INFO'].split('/static/') if p]
#             if len(items) == 1:
#                 static_file = items[-1]
#                 if static_file in self.static_files:
#                     start_response('200 OK', [('Content-Type', 'application/javascript;charset=utf-8'),('Access-Control-Allow-Origin','*')])
#                     return [self.static_files[static_file]]

#                 host = environ.get('HTTP_HOST')
#                 file_path = j.sal.fs.joinPaths(self.static_files_path, static_file)
#                 if j.sal.fs.exists(file_path):
#                     self.static_files[static_file] = j.sal.fs.readFile(file_path).replace('%%host%%', host).encode('utf-8')
#                     start_response('200 OK', [('Content-Type', 'application/javascript;charset=utf-8'),('Access-Control-Allow-Origin','*')])
#                     return [self.static_files[static_file]]
            
#             start_response('404 NOT FOUND', [])
#             return []


# websocket = environ.get('wsgi.websocket')
# if not websocket:
#     return []
# addr = '{0}:{1}'.format(environ['REMOTE_ADDR'],environ['REMOTE_PORT'])
# handler = WebsocketRequestHandler(self.instance, self.cmds, self.classes, self.cmds_meta)
# handler.handle(websocket, addr)
# return []