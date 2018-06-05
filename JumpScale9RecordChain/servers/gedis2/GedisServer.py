import sys
import os
from js9 import j
import signal
import gevent
import gevent.signal
from gevent.pool import Pool
from gevent.server import StreamServer
from .protocol import CommandParser, ResponseWriter

from .GedisCmds import GedisCmds


JSConfigBase = j.tools.configmanager.base_class_config


class GedisServer(StreamServer, JSConfigBase):
    TEMPLATE = """
    addr = "localhost"
    port = "9900"
    ssl = false
    adminsecret_ = ""
    path = ""
    namespace = ""
    """

    def __init__(
        self,
        instance,
        data={},
        parent=None,
        interactive=False,
        template=None
    ):

        JSConfigBase.__init__(
            self,
            instance=instance,
            data=data,
            parent=parent,
            template=template or self.TEMPLATE, # default config if template is None
            interactive=interactive
        )



        self.db = None
        self._sig_handler = []
        self.cmds_meta = {}
        self.classes = {}
        self.cmds = {}
        self.schema_urls = []
        self.serializer = None
        self._inited = False

        host = self.config.data["addr"]
        port = int(self.config.data["port"])

        self.address = '{}:{}'.format(host, port)

        if self.config.data['ssl']:
            self.logger.info("ssl enabled, keys in %s" %
                             self.ssl_priv_key_path)
            self.sslkeys_generate()

            self.server = StreamServer(
                (host, port), spawn=Pool(), handle=self.__handle_connection, keyfile=self.ssl_priv_key_path, certfile=self.ssl_cert_path)
        else:
            self.server = StreamServer(
                (host, port), spawn=Pool(), handle=self.__handle_connection)

        j.servers.gedis2.latest = self        

    def sslkeys_generate(self):

        res = j.sal.ssl.ca_cert_generate(j.sal.fs.getDirName(self.config.path))
        if res:
            self.logger.info("generated sslkeys for gedis in %s" %
                             self.config.path)

    @property
    def ssl_priv_key_path(self):
        p = j.sal.fs.getDirName(self.config.path) + "ca.key"
        if self.config.data["ssl"]:
            return p

    @property
    def ssl_cert_path(self):
        p = j.sal.fs.getDirName(self.config.path) + "ca.crt"
        if self.config.data["ssl"]:
            return p

    def __handle_connection(
        self,
        socket,
        address
    ):
        self.logger.info('connection from {}'.format(address))
        parser = CommandParser(socket)
        response = ResponseWriter(socket)

        try:
            while True:
                request = parser.read_request()

                if not request: # empty string request
                    response.error('Empty request body .. probably this is a (TCP port) checking query')
                    continue

                # Get CMD
                cmd = request[0]
                redis_cmd = cmd.decode("utf-8").lower()
                cmd , err = self.get_command(redis_cmd)
                params = None # CMD params

                if err:
                    response.error(err)
                    continue

                if cmd.schema_in:

                    if len(request) < 2:
                        response.error("need to have arguments, none given")
                        continue

                    if len(request) > 2:
                        response.error("more than 1 argument given, needs to be binary capnp message or json")
                        continue 
                    o = cmd.schema_in.get(capnpbin=request[1])
                    params=o.ddict

                    if "id" in params:
                        params.pop("id")

                    if cmd.schema_out:
                        params["schema_out"] = cmd.schema_out
                else:
                    if len(request) > 1:
                        params = request[1:]

                # execute command callback
                self.logger.debug("execute command callback:%s:%s" % (cmd, params))
                result = None

                try:
                    if params is None:
                        result = cmd.method()
                    elif j.data.types.list.check(params):
                        result = cmd.method(*params)
                    else:
                        result = cmd.method(**params)
                except Exception as e:

                    eco = j.errorhandler.parsePythonExceptionObject(e)
                    msg = str(eco)
                    msg += "\nCODE:%s:%s\n"%(cmd.namespace,cmd.name)
                    self.logger.error(msg)
                    response.error(msg)
                    continue

                self.logger.debug("Callback done and result {} , type {}".format(result, type(result)))

                self.logger.debug(
                    "response:{}:{}:{}".format(address, cmd, result))

                if cmd.schema_out:
                    result = result.data

                response.encode(result)

        except ConnectionError as err:
            self.logger.error('connection error: {}'.format(str(err)))
        finally:
            parser.on_disconnect()
            self.logger.info('close connection from {}'.format(address))

    def init(self):
        self.logger.info("init server")
        self._sig_handler.append(gevent.signal(signal.SIGINT, self.stop))
        self.logger.info("start server")

        # add the cmds to the server (from generated modules)
        path_server = self.server_path

        for item in j.sal.fs.listFilesInDir(path_server,filter="*.py",exclude=["__*"]):
            namespace_base = self.config.data["namespace"]
            if not namespace_base:
                raise RuntimeError("namespace cannot be empty")
            if namespace_base[-1] is not ".":
                namespace_base+="."                
            namespace = namespace_base+j.sal.fs.getBaseName(item)[:-3].lower()
            self.cmds_add(namespace, path=item)
        self._inited = True

    def start(self, schema_path="", reset=False):

        j.data.bcdb.db_start(
            self.instance,
            adminsecret=self.config.data["adminsecret_"],
            reset=reset
        )

        db = j.data.bcdb.get(self.instance)
        db.tables_get(schema_path)  # will get it from current path
        self.db = db
        # tables are now in db.tables as dict

        self.generate(reset=reset)

        if self._inited is False:
            self.init()

        self.server.serve_forever()

    def stop(self):
        """
        stop receiving requests and close the server
        """
        # prevent the signal handler to be called again if
        # more signal are received
        for h in self._sig_handler:
            h.cancel()

        self.logger.info('stopping server')
        self.server.stop()

    def cmds_add(self, namespace, path=None, class_=None):
        self.logger.debug("cmds_add:%s:%s"%(namespace , path))
        if path is not None:
            classname = j.sal.fs.getBaseName(path).split(".", 1)[0]
            dname = j.sal.fs.getDirName(path)
            if dname not in sys.path:
                sys.path.append(dname)

            #TODO:*1 use imp... instead
            exec("from %s import %s" % (classname, classname))
            class_ = eval(classname)

        self.cmds_meta[namespace] = GedisCmds(self, namespace=namespace, class_=class_)
        self.classes[namespace] =class_()

    @property
    def server_path(self):
        j.data.schema.instance = self.instance
        path = os.path.join(j.dirs.VARDIR, 'codegen', 'gedis', self.instance, 'server')
        if not j.sal.fs.exists(path):
            j.sal.fs.createDir(path)
        if not path in sys.path:
            sys.path.append(path)
        return path

    def generate(self,db=None, reset=False):
        
        db = db or self.db

        path = self.server_path
        self.logger.debug("codegendir: %s" % path)

        if path not in sys.path:
            sys.path.append(path)

        j.sal.fs.touch(os.path.join(path, '__init__.py'))

        # copy the templates in the local server dir
        for item in ["system"]:

            dest = os.path.join(path, "%s.py" % item)
            if reset or not j.sal.fs.exists(dest):
                src = os.path.join(j.servers.gedis2._path, "templates", '%s.py' % item)
                j.sal.fs.copyFile(src, dest)

        # Generate & models (name spaces) from schema
        for namespace,table in db.tables.items():
            # url = table.schema.url.replace(".","_")
            dest = os.path.join(path, "model_%s.py" % namespace)
            if reset or not j.sal.fs.exists(dest):
                code = j.servers.gedis2.code_model_template.render(obj= table.schema)
                j.sal.fs.writeFile(dest,code)
            self.schema_urls.append(table.schema.url)

    @property
    def namespace(self):
        return self.config.data["namespace"]

    def get_command(self, cmd):

        if cmd in self.cmds:
            return self.cmds[cmd], ''

        self.logger.debug('(%s) command cache miss')

        if not '.' in cmd:
            return None, 'Invalid command (%s) : model is missing. proper format is {model}.{cmd}'

        pre, post = cmd.split(".", 1)

        namespace = self.namespace + "." + pre

        if namespace not in self.classes:
            return None,"Cannot find namespace:%s "% (namespace)

        if namespace not in self.cmds_meta:
            return None,"Cannot find namespace:%s"%(namespace)

        meta = self.cmds_meta[namespace]

        if not post in meta.cmds:
            return None,"Cannot find method with name:%s in namespace:%s"%(post,namespace)
        
        cmd_obj = meta.cmds[post]

        try:
            cl = self.classes[namespace]
            m = eval("cl.%s"%(post))
        except Exception as e:
            return None,"Could not execute code of method '%s' in namespace '%s'\n%s"%(pre,namespace,e)

        cmd_obj.method = m

        self.cmds[cmd] = cmd_obj

        return self.cmds[cmd], ""
