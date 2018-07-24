import sys
import os
from js9 import j
import signal
import gevent
import gevent.signal
from gevent.pool import Pool
from gevent.server import StreamServer
from .handlers import WebsocketRequestHandler, RedisRequestHandler
from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi

from .protocol import RedisCommandParser, RedisResponseWriter, WebsocketsCommandParser, WebsocketResponseWriter
from .GedisCmds import GedisCmds

JSConfigBase = j.tools.configmanager.base_class_config


TEMPLATE = """
    host = "localhost"
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

        self.db = None
        self.static_files = {}
        self._sig_handler = []
        self.cmds_meta = {}
        self.classes = {}
        self.cmds = {}
        self.schema_urls = []
        self.serializer = None
        self._inited = False
        self.ssl_priv_key_path = None
        self.ssl_cert_path = None
        self.host = self.config.data["host"]
        self.port = int(self.config.data["port"])
        self.websockets_port = int(self.config.data["websockets_port"])
        self.address = '{}:{}'.format(self.host, self.port)
        self.ssl = self.config.data["ssl"]
        self.web_client_code = None

        j.servers.gedis.latest = self

        # create dirs for generated codes
        self.code_generated_dir = j.sal.fs.joinPaths(j.dirs.VARDIR, "codegen", "gedis", instance, "server")
        j.sal.fs.createDir(self.code_generated_dir)
        j.sal.fs.touch(j.sal.fs.joinPaths(self.code_generated_dir, '__init__.py'))

        if self.code_generated_dir not in sys.path:
            sys.path.append(self.code_generated_dir)

        # make sure apps dir is created if not exists
        self.app_dir = self.config.data["app_dir"]
        


        if self.app_dir not in sys.path:
            sys.path.append(self.app_dir)

        # make sure static dir exists
        self.static_files_path = j.sal.fs.joinPaths(self.code_generated_dir, 'static')
        j.sal.fs.createDir(self.static_files_path)

        # make sure app dir is created if not exists
        self.app_dir = j.sal.fs.joinPaths(self.app_dir, self.instance)
        j.sal.fs.createDir(self.app_dir)

        p = j.sal.fs.joinPaths(self.app_dir, '__init__.py')

        if not j.sal.fs.exists(p):
            j.sal.fs.touch(p)

        if self.app_dir not in sys.path:
            sys.path.append(self.app_dir)

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
            self.websocket_server = pywsgi.WSGIServer(('0.0.0.0', self.websockets_port), self.websocketapp, handler_class=WebSocketHandler)
        else:
            self.redis_server = StreamServer(
                (self.host, self.port),
                spawn=Pool(),
                handle=RedisRequestHandler(self.instance, self.cmds, self.classes, self.cmds_meta).handle
            )
            self.websocket_server = pywsgi.WSGIServer(('0.0.0.0', self.websockets_port), self.websocketapp, handler_class=WebSocketHandler)

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

    def websocketapp(self, environ, start_response):
        if '/static/' in environ['PATH_INFO']:
            items = [p for p in environ['PATH_INFO'].split('/static/') if p]
            if len(items) == 1:
                static_file = items[-1]
                if not static_file in self.static_files:
                    host = environ.get('HTTP_HOST')
                    file_path = j.sal.fs.joinPaths(self.static_files_path, static_file)
                    if j.sal.fs.exists(file_path):
                        self.static_files[static_file] = j.sal.fs.readFile(file_path).replace('%%host%%', host).encode('utf-8')
                        start_response('200 OK', [])
                        return [self.static_files[static_file]]
            start_response('404 NOT FOUND', [])
            return []

        websocket = environ.get('wsgi.websocket')
        if not websocket:
            return []
        addr = '{0}:{1}'.format(environ['REMOTE_ADDR'],environ['REMOTE_PORT'])
        handler = WebsocketRequestHandler(self.instance, self.cmds, self.classes, self.cmds_meta)
        handler.handle(websocket, addr)
        return []

    def init(self):
        # add the cmds to the server (from generated dir + app_dir)
        namespace_base = self.instance
        files = j.sal.fs.listFilesInDir(self.code_generated_dir, filter="*.py", exclude=["__*", "test*"]) + j.sal.fs.listFilesInDir(self.app_dir, filter="*.py", exclude=["__*", "test*"])
        for item in files:
            namespace = namespace_base + '.' + j.sal.fs.getBaseName(item)[:-3].lower()
            self.cmds_add(namespace, path=item)

        # generate web client
        commands = []

        for nsfull, cmds_ in self.cmds_meta.items():
            if 'model_' in nsfull:
                continue
            commands.append(cmds_)

        code = j.servers.gedis.js_client_template.render(commands=commands)
        dest = os.path.join(self.code_generated_dir, 'static', 'client.js')
        j.sal.fs.writeFile(dest, code)

        self.web_client_code = code
        self._inited = True

    def _start(self, db=None,reset=False):

        if not db:
            j.data.bcdb.db_start(self.instance, adminsecret=self.config.data["adminsecret_"], reset=reset)
            db = j.data.bcdb.get(self.instance)
            db.tables_get(self.app_dir)
        self.db = db

        # copy the templates in the local server dir
        for item in ["system"]:
            dest = j.sal.fs.joinPaths(self.code_generated_dir, "%s.py" % item)
            if reset or not j.sal.fs.exists(dest):
                src = j.sal.fs.joinPaths(j.servers.gedis._path, "templates", '%s.py' % item)
                j.sal.fs.copyFile(src, dest)

        # Generate models & populate self.schema_urls
        for namespace, table in db.tables.items():
            # url = table.schema.url.replace(".","_")
            dest = j.sal.fs.joinPaths(self.code_generated_dir, "model_%s.py" % namespace)
            if reset or not j.sal.fs.exists(dest):
                code = j.servers.gedis.code_model_template.render(obj=table.schema)
                j.sal.fs.writeFile(dest, code)
            self.schema_urls.append(table.schema.url)

        # load commands if not loaded before
        if self._inited is False:
            self.init()

        self._sig_handler.append(gevent.signal(signal.SIGINT, self.stop))

        from gevent import monkey
        monkey.patch_thread()
        import threading

        t = threading.Thread(target=self.websocket_server.serve_forever)
        t.setDaemon(True)
        t.start()
        self.logger.info("start Server on {0} - PORT: {1} - WEBSOCKETS PORT: {2}".format(self.host, self.port, self.websockets_port))
        self.redis_server.serve_forever()

    def start(self, db=None,reset=False, background=True):
        if not background:
            self._start(db, reset)
        else:
            cmd = "js9 'x=j.servers.gedis.get(instance=\"%s\");x._start(reset=%s)'" % (self.instance, reset)
            j.tools.tmux.execute(
                cmd,
                session='main',
                window='gedis_%s' % self.instance,
                pane='main',
                session_reset=False,
                window_reset=True
            )

            res = j.sal.nettools.waitConnectionTest("localhost", int(self.config.data["port"]), timeoutTotal=1000)
            if res == False:
                raise RuntimeError("Could not start gedis server on port:%s" % int(self.config.data["port"]))
            self.logger.info("gedis server '%s' started" % self.instance)

    def stop(self):
        """
        stop receiving requests and close the server
        """
        # prevent the signal handler to be called again if
        # more signal are received
        for h in self._sig_handler:
            h.cancel()

        self.logger.info('stopping server')
        self.redis_server.stop()

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

    def __repr__(self):
        return '<Gedis Server address=%s  app_dir=%s generated_code_dir=%s)' % (self.address, self.app_dir, self.code_generated_dir)

    __str__ = __repr__

