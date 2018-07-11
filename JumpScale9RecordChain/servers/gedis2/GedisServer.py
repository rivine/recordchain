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


TEMPLATE = """
    host = "localhost"
    port = "9900"
    ssl = false
    adminsecret_ = ""
    apps_dir = ""
    """


class GedisServer(StreamServer, JSConfigBase):
    def __init__(self, instance, data={}, parent=None, interactive=False, template=None):
        JSConfigBase.__init__(self, instance=instance, data=data, parent=parent, template=template or TEMPLATE, interactive=interactive)

        self.db = None
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
        self.address = '{}:{}'.format(self.host, self.port)
        self.ssl = self.config.data["ssl"]

        j.servers.gedis2.latest = self

        # create dirs for generated codes
        self.code_generated_dir = j.sal.fs.joinPaths(j.dirs.VARDIR, "codegen", "gedis2", instance, "server")
        j.sal.fs.createDir(self.code_generated_dir)
        j.sal.fs.touch(j.sal.fs.joinPaths(self.code_generated_dir, '__init__.py'))

        if self.code_generated_dir not in sys.path:
            sys.path.append(self.code_generated_dir)

        # make sure apps dir is created if not exists
        self.apps_dir = self.config.data["apps_dir"] or j.sal.fs.joinPaths(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'apps')
        j.sal.fs.createDir(self.apps_dir)
        j.sal.fs.touch(j.sal.fs.joinPaths(self.apps_dir, '__init__.py'))

        if self.apps_dir not in sys.path:
            sys.path.append(self.apps_dir)

        # make sure app dir is created if not exists
        self.app_dir = j.sal.fs.joinPaths(self.apps_dir, self.instance)
        j.sal.fs.createDir(self.app_dir)
        j.sal.fs.touch(j.sal.fs.joinPaths(self.app_dir, '__init__.py'))

        if self.app_dir not in sys.path:
            sys.path.append(self.app_dir)

        if self.ssl:
            self.ssl_priv_key_path, self.ssl_cert_path = self.sslkeys_generate()

            # Server always supports SSL
            # client can use to talk to it in SSL or not
            self.server = StreamServer(
                (self.host, self.port),
                spawn=Pool(),
                handle=self.__handle_connection,
                keyfile=self.ssl_priv_key_path,
                certfile=self.ssl_cert_path
            )
        else:
            self.server = StreamServer(
                (self.host, self.port),
                spawn=Pool(),
                handle=self.__handle_connection)

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

    def __handle_connection(self, socket, address):
        self.logger.info('connection from {}'.format(address))
        parser = CommandParser(socket)
        response = ResponseWriter(socket)

        try:
            while True:
                request = parser.read_request()

                if not request:  # empty string request
                    response.error('Empty request body .. probably this is a (TCP port) checking query')
                    continue

                cmd = request[0]
                redis_cmd = cmd.decode("utf-8").lower()

                cmd , err = self.get_command(redis_cmd)
                if err is not "":
                    response.error(err)
                    continue
                if cmd.schema_in:
                    if len(request)<2:
                        response.error("need to have arguments, none given")
                        continue
                    if len(request) > 2:
                        cmd.schema_in.properties
                        print("more than 1 input")
                        response.error("more than 1 argument given, needs to be binary capnp message or json")
                        continue

                    id, data = j.data.serializer.msgpack.loads(request[1])
                    o=cmd.schema_in.get(capnpbin=data)
                    if id:
                        o.id = id
                    args = [a.strip() for a in cmd.cmdobj.args.split(',')]
                    if 'schema_out' in args:
                        args.remove('schema_out')
                    params = {}
                    schema_dict = o.ddict
                    if len(args) == 1:
                        if args[0] in schema_dict:
                            params.update(schema_dict)
                        else:
                            params[args[0]] = o
                    else:
                        params.update(schema_dict)

                    if cmd.schema_out:
                        params["schema_out"] = cmd.schema_out
                else:
                    if len(request) > 1:
                        params = request[1:]
                        if cmd.schema_out:
                            params.append(cmd.schema_out)
                    else:
                        params = None

                self.logger.debug("execute command callback:%s:%s"%(cmd,params))
                result = None
                try:
                    if params is None:
                        result = cmd.method()
                    elif j.data.types.list.check(params):
                        result = cmd.method(*params)
                    else:
                        result = cmd.method(**params)
                    self.logger.debug("Callback done and result {} , type {}".format(result, type(result)))
                except Exception as e:
                    print("exception in redis server")
                    eco = j.errorhandler.parsePythonExceptionObject(e)
                    msg = str(eco)
                    msg += "\nCODE:%s:%s\n"%(cmd.namespace,cmd.name)
                    print (msg)
                    response.error(e.args[:100])
                    continue
                self.logger.debug(
                    "response:{}:{}:{}".format(address, cmd, result))

                if cmd.schema_out:
                    result=result.data
                response.encode(result)

        except ConnectionError as err:
            self.logger.info('connection error: {}'.format(str(err)))
        finally:
            parser.on_disconnect()
            self.logger.info('close connection from {}'.format(address))

    def get_command(self, cmd):
        if cmd in self.cmds:
            return self.cmds[cmd], ''

        self.logger.debug('(%s) command cache miss')

        if not '.' in cmd:
            return None, 'Invalid command (%s) : model is missing. proper format is {model}.{cmd}'

        pre, post = cmd.split(".", 1)

        namespace = self.instance + "." + pre

        if namespace not in self.classes:
            return None, "Cannot find namespace:%s " % (namespace)

        if namespace not in self.cmds_meta:
            return None, "Cannot find namespace:%s" % (namespace)

        meta = self.cmds_meta[namespace]

        if not post in meta.cmds:
            return None, "Cannot find method with name:%s in namespace:%s" % (post, namespace)

        cmd_obj = meta.cmds[post]

        try:
            cl = self.classes[namespace]
            m = eval("cl.%s" % (post))
        except Exception as e:
            return None, "Could not execute code of method '%s' in namespace '%s'\n%s" % (pre, namespace, e)

        cmd_obj.method = m

        self.cmds[cmd] = cmd_obj

        return self.cmds[cmd], ""

    def init(self):
        # add the cmds to the server (from generated dir + app_dir)
        namespace_base = self.instance
        files = j.sal.fs.listFilesInDir(self.code_generated_dir, filter="*.py", exclude=["__*"]) + j.sal.fs.listFilesInDir(self.app_dir, filter="*.py", exclude=["__*"])
        for item in files:
            namespace = namespace_base + '.' + j.sal.fs.getBaseName(item)[:-3].lower()
            self.cmds_add(namespace, path=item)

        # generate web client
        commands = []

        for nsfull, cmds_ in self.cmds_meta.items():
            if 'model_' in nsfull:
                continue
            commands.append(cmds_)

        code = j.servers.gedis2.js_client_template.render(commands=commands)
        dest = os.path.join(self.code_generated_dir, 'client.js')
        j.sal.fs.writeFile(dest, code)
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
                src = j.sal.fs.joinPaths(j.servers.gedis2._path, "templates", '%s.py' % item)
                j.sal.fs.copyFile(src, dest)

        # Generate models & populate self.schema_urls
        for namespace, table in db.tables.items():
            # url = table.schema.url.replace(".","_")
            dest = j.sal.fs.joinPaths(self.code_generated_dir, "model_%s.py" % namespace)
            if reset or not j.sal.fs.exists(dest):
                code = j.servers.gedis2.code_model_template.render(obj=table.schema)
                j.sal.fs.writeFile(dest, code)
            self.schema_urls.append(table.schema.url)

        # load commands if not loaded before
        if self._inited is False:
            self.init()

        self._sig_handler.append(gevent.signal(signal.SIGINT, self.stop))
        self.logger.info("start server")
        self.server.serve_forever()

    def start(self, db=None,reset=False, background=True):
        if not background:
            self._start(db, reset)
        else:
            cmd = "js9 'x=j.servers.gedis2.get(instance=\"%s\");x._start(reset=%s)'" % (self.instance, reset)
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
        self.server.stop()

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

