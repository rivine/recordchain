import sys
import os
from js9 import j
import signal
import gevent
import gevent.signal
from gevent.pool import Pool
from gevent.server import StreamServer
from .handlers import WebsocketRequestHandler, RedisRequestHandler
# from geventwebsocket.handler import WebSocketHandler
from .JSAPIServer import JSAPIServer
from .GedisChatBot import GedisChatBotFactory


from .protocol import RedisCommandParser, RedisResponseWriter, WebsocketsCommandParser, WebsocketResponseWriter
from .GedisCmds import GedisCmds

JSConfigBase = j.tools.configmanager.base_class_config


TEMPLATE = """
    host = "0.0.0.0"
    port = "9900"
    websockets_port = "9901"
    ssl = false
    adminsecret_ = ""
    app_dir = ""
    zdb_instance = ""
    """


class GedisServer(StreamServer, JSConfigBase):
    def __init__(self, instance, data={}, parent=None, interactive=False, template=None):
        JSConfigBase.__init__(self, instance=instance, data=data, parent=parent, template=template or TEMPLATE, interactive=interactive)

        self.static_files = {}
        self._sig_handler = []
        self.cmds_meta = {}
        self.classes = {}
        self.cmds = {}
        self.schema_urls = []
        self.serializer = None

        self.ssl_priv_key_path = None
        self.ssl_cert_path = None

        self.host = "0.0.0.0"#self.config.data["host"]
        self.port = int(self.config.data["port"])
        self.websockets_port = int(self.config.data["websockets_port"])
        self.address = '{}:{}'.format(self.host, self.port)
        self.app_dir = self.config.data["app_dir"]
        self.ssl = self.config.data["ssl"]

        self.web_client_code = None
        self.code_generated_dir = j.sal.fs.joinPaths(j.dirs.VARDIR, "codegen", "gedis", self.instance, "server")

        self.jsapi_server = JSAPIServer()
        self.chatbot = GedisChatBotFactory(ws=self)
        
        self.init()

    def sslkeys_generate(self):
        if self.ssl:
            path = os.path.dirname(self.code_generated_dir)
            res = j.sal.ssl.ca_cert_generate(path)
            if res:
                self.logger.info("generated sslkeys for gedis in %s" % path)
            else:
                self.logger.info('using existing key and cerificate for gedis @ %s' % path)
            key = j.sal.fs.joinPaths(path, 'ca.key')
            cert = j.sal.fs.joinPaths(path, 'ca.crt')
            return key, cert

    def init(self):
        
        #hook to allow external servers to find this gedis
        j.servers.gedis.latest = self        

        # create dirs for generated codes and make sure is empty
        for cat in ["server","client"]:
            code_generated_dir = j.sal.fs.joinPaths(j.dirs.VARDIR, "codegen", "gedis", self.instance, cat)
            j.sal.fs.remove(code_generated_dir)
            j.sal.fs.createDir(code_generated_dir)
            j.sal.fs.touch(j.sal.fs.joinPaths(code_generated_dir, '__init__.py'))

        #now add the one for the server
        if self.code_generated_dir not in sys.path:
            sys.path.append(self.code_generated_dir)

        # make sure apps dir is created if not exists
        if self.app_dir.strip() is "":
            raise RuntimeError("appdir cannot be empty")
        j.sal.fs.createDir(self.app_dir)
        
        #copies the base from the jumpscale lib to the appdir
        self.logger.debug("copy base to:%s"%self.app_dir )
        #make sure reset stays false

        j.tools.jinja2.copy_dir_render("%s/base"%j.servers.gedis.path,self.app_dir ,overwriteFiles=True, render=False, reset=False, \
            j=j, config=self.config.data, instance=self.instance)     

        # add the cmds to the server (from generated dir + app_dir)
        self.bcdb_init() #make sure we know the schemas
        self.code_generate_model_actors() #make sure we have the actors generated for the model, is in server on code generation dir

        #now in code generation dir we have the actors generated for the model
        #load the commands into the namespace of the server (self.cmds_add)
        files = j.sal.fs.listFilesInDir(self.code_generated_dir,"server", filter="*.py", exclude=["__*", "test*"]) 
        files += j.sal.fs.listFilesInDir(self.app_dir+"/actors", filter="*.py", exclude=["__*"])
        for item in files:
            namespace = self.instance + '.' + j.sal.fs.getBaseName(item)[:-3].lower()
            self.logger.debug("cmds generated add:%s"%item)
            self.cmds_add(namespace, path=item)

        self.code_generate_js_client()

        self._servers_init()

        self._inited = True        

    def bcdb_init(self):
        """
        result is schema's are loaded & known, can be accesed in self.bcdb
        """
        zdb = j.clients.zdb.get(self.config.data["zdb_instance"])
        bcdb = j.data.bcdb.get(zdb)
        bcdb.tables_get(j.sal.fs.joinPaths(self.app_dir, 'schemas'))
        self.bcdb = bcdb     

    def code_generate_model_actors(self):
        """
        generate the actors (methods to work with model) for the model and put in code generated dir
        """
        reset=True
        self.logger.info("Generate models & populate self.schema_urls")
        self.logger.info("in: %s"%self.code_generated_dir)
        for namespace, table in self.bcdb.tables.items():
            # url = table.schema.url.replace(".","_")
            self.logger.info("generate model: model_%s.py" % namespace)
            dest = j.sal.fs.joinPaths(self.code_generated_dir, "model_%s.py" % namespace)
            if reset or not j.sal.fs.exists(dest):
                find_args = ''.join(["{0}={1},".format(p.name, p.default_as_python_code) for p in table.schema.properties if p.index]).strip(',')
                kwargs = ''.join(["{0}={0},".format(p.name, p.name) for p in table.schema.properties if p.index]).strip(',')
                code = j.tools.jinja2.file_render("%s/templates/actor_model_server.py"%(j.servers.gedis.path),
                    obj=table.schema, find_args=find_args, dest=dest, kwargs=kwargs)
            self.schema_urls.append(table.schema.url)

    def code_generate_js_client(self):
        """
        "generate the code for the javascript browser
        """
        # generate web client
        commands = []

        for nsfull, cmds_ in self.cmds_meta.items():
            if 'model_' in nsfull:
                continue
            commands.append(cmds_)        
        self.code_js_client = j.tools.jinja2.file_render("%s/templates/client.js"%(j.servers.gedis.path),commands=commands,write=False)

    def _servers_init(self):
        if self.ssl:
            self.ssl_priv_key_path, self.ssl_cert_path = self.sslkeys_generate()
            # Server always supports SSL
            # client can use to talk to it in SSL or not
            self.redis_server = StreamServer(
                (self.host, self.port),
                spawn=Pool(),
                handle=RedisRequestHandler(self.instance, self.cmds, self.classes, self.cmds_meta).handle,
                keyfile=self.ssl_priv_key_path,
                certfile=self.ssl_cert_path
            )
            #NO SSL ON WEBSOCKET SERVER? TODO:*1
            # self.websocket_server = pywsgi.WSGIServer(('0.0.0.0', self.websockets_port), self.websocketapp, handler_class=WebSocketHandler)
        else:
            self.redis_server = StreamServer(
                (self.host, self.port),
                spawn=Pool(),
                handle=RedisRequestHandler(self.instance, self.cmds, self.classes, self.cmds_meta).handle
            )

        self.websocket_server = self.jsapi_server.websocket_server  #is the server we can use     
        self.jsapi_server.code_js_client = self.code_js_client
        self.jsapi_server.instance = self.instance
        self.jsapi_server.cmds = self.cmds
        self.jsapi_server.classes = self.classes
        self.jsapi_server.cmds_meta = self.cmds_meta

    def cmds_add(self, namespace, path=None, class_=None):
        self.logger.debug("cmds_add:%s:%s"%(namespace,path))
        if path is not None:
            classname = j.sal.fs.getBaseName(path).split(".", 1)[0]
            dname = j.sal.fs.getDirName(path)
            if dname not in sys.path:
                sys.path.append(dname)
            exec("from %s import %s" % (classname, classname))
            class_ = eval(classname)
        self.cmds_meta[namespace] = GedisCmds(self, namespace=namespace, class_=class_)
        self.classes[namespace] =class_()

    def client_get(self):

        data ={}
        data["host"] = self.config.data["host"]
        data["port"] = self.config.data["port"]
        data["adminsecret_"] = self.config.data["adminsecret_"]
        data["ssl"] = self.config.data["ssl"]
        
        return j.clients.gedis.get(instance=self.instance, data=data, reset=False)

    def __repr__(self):
        return '<Gedis Server address=%s  app_dir=%s generated_code_dir=%s)' % (self.address, self.app_dir, self.code_generated_dir)

    __str__ = __repr__






    # def _start(self):

        # self._sig_handler.append(gevent.signal(signal.SIGINT, self.stop))

        # from gevent import monkey
        # monkey.patch_thread() #TODO:*1 dirty hack, need to use gevent primitives, suggest to add flask server
        # import threading

        # if self.ssl:
        #     self.ssl_priv_key_path, self.ssl_cert_path = self.sslkeys_generate()

        #     # Server always supports SSL
        #     # client can use to talk to it in SSL or not
        #     self.redis_server = StreamServer(
        #         (self.host, self.port),
        #         spawn=Pool(),
        #         handle=RedisRequestHandler(self.instance, self.cmds, self.classes, self.cmds_meta).handle,
        #         keyfile=self.ssl_priv_key_path,
        #         certfile=self.ssl_cert_path
        #     )
        #     self.websocket_server = pywsgi.WSGIServer(('0.0.0.0', self.websockets_port), self.websocketapp, handler_class=WebSocketHandler)
        # else:
        #     self.redis_server = StreamServer(
        #         (self.host, self.port),
        #         spawn=Pool(),
        #         handle=RedisRequestHandler(self.instance, self.cmds, self.classes, self.cmds_meta).handle
        #     )
        #     



        # t = threading.Thread(target=self.websocket_server.serve_forever)
        # t.setDaemon(True)
        # t.start()
        # self.logger.info("start Server on {0} - PORT: {1} - WEBSOCKETS PORT: {2}".format(self.host, self.port, self.websockets_port))
        # self.redis_server.serve_forever()

    # def gevent_websocket_server_get():
    #     self.websocket_server = pywsgi.WSGIServer(('0.0.0.0', 9999), self.websocketapp, handler_class=WebSocketHandler)



    
    # def start(self, reset=False, background=True):
    #     if not background:
    #         self._start()
    #     else:
    #         cmd = "js9 'x=j.servers.gedis.get(instance=\"%s\");x._start()'" % (self.instance)
    #         j.tools.tmux.execute(
    #             cmd,
    #             session='main',
    #             window='gedis_%s' % self.instance,
    #             pane='main',
    #             session_reset=False,
    #             window_reset=True
    #         )

    #         res = j.sal.nettools.waitConnectionTest("localhost", int(self.config.data["port"]), timeoutTotal=1000)
    #         if res == False:
    #             raise RuntimeError("Could not start gedis server on port:%s" % int(self.config.data["port"]))
    #         self.logger.info("gedis server '%s' started" % self.instance)

    # def stop(self):
    #     """
    #     stop receiving requests and close the server
    #     """
    #     # prevent the signal handler to be called again if
    #     # more signal are received
    #     for h in self._sig_handler:
    #         h.cancel()

    #     self.logger.info('stopping server')
    #     self.redis_server.stop()