
from js9 import j
import signal
import gevent
import gevent.signal
from gevent.pool import Pool
from gevent.server import StreamServer
from .protocol import CommandParser, ResponseWriter
import inspect
import imp
import sys
from .GedisCmds import GedisCmds

TEMPLATE = """
addr = "localhost"
port = "9900"
ssl = false
adminsecret_ = ""
path = ""
"""
JSConfigBase = j.tools.configmanager.base_class_config


class GedisServer(StreamServer, JSConfigBase):

    def __init__(self, instance, data={}, parent=None, interactive=False, template=None):
        """
        """
        if not template:
            template = TEMPLATE
        JSConfigBase.__init__(self, instance=instance, data=data,
                              parent=parent, template=template, interactive=interactive)
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

        self._sig_handler = []

        self.cmds = {}
            
        # self.cmds_add(namespace="system", class_=GedisServerBase)

        j.servers.gedis.latest = self

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

    # def register_command(self, cmd, callback):

    #     self.logger.info("add cmd %s" % cmd)
    #     content = inspect.getsource(callback)

    #     #remove the self. if written as class style
    #     lines = content.splitlines()
    #     content = ""
    #     for line in lines:
    #         line = line.replace("self,", "")
    #         content = content + line[4:] + "\n"

    #     if not j.sal.fs.exists(path=self._cmds_path):
    #         j.sal.fs.writeFile(self._cmds_path, contents=content)
    #     else:
    #         __cmds = imp.load_source(name="cmds.py", pathname=self._cmds_path)
    #         if cmd+"_cmd" not in __cmds.__dir__():
    #             j.sal.fs.writeFile(self._cmds_path, contents='\n' + content, append=True)

    def __handle_connection(self, socket, address):
        self.logger.info('connection from {}'.format(address))
        parser = CommandParser(socket)
        response = ResponseWriter(socket)

        try:
            while True:
                request = parser.read_request()
                cmd = request[0]
                if cmd.decode("utf-8")+"_cmd".lower() not in (command.lower() for command in self._cmds.__dir__()):
                    response.error('command not supported')
                    continue

                # execute command callback
                print("execute command callback")
                from IPython import embed;embed(colors='Linux')
                jhg
                result = ""
                try:
                    result = getattr(self._cmds, cmd.decode("utf-8")+"_cmd")(request)
                    self.logger.debug("Callback done and result {} , type {}".format(result, type(result)))
                except Exception as e:
                    print("exception in redis server")
                    eco = j.errorhandler.parsePythonExceptionObject(e)
                    response.error(str(eco))
                    continue
                self.logger.debug(
                    "response:{}:{}:{}".format(address, cmd, result))
                response.encode(result)

        except ConnectionError as err:
            self.logger.info('connection error: {}'.format(str(err)))
        finally:
            parser.on_disconnect()
            self.logger.info('close connection from {}'.format(address))

    def start(self):
        self.logger.info("init server")
        j.logger.enabled = False
        self._logger = None

        self._sig_handler.append(gevent.signal(signal.SIGINT, self.stop))

        self.logger.info("start server")
        # SHOULD NOT IMPLEMENT BACKGROUND HERE HAS BEEN DONE AT FACTORY LEVEL
        # if background:
        #     from multiprocessing import Process
        #     p = Process(target=self.server.serve_forever)
        #     p.start()
        # else:
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

    # def _cmds_add(self, namespace, path=None, class_=None):

    #     if path is not None:
    #         classname = j.sal.fs.getBaseName(path).split(".", 1)[0]
    #         dname = j.sal.fs.getDirName(path)
    #         if dname not in sys.path:
    #             sys.path.append(dname)

    #         exec("from .%s import %s" % (classname, classname))
    #         class_ = eval(classname)

    #     self.cmds[namespace] = GedisCmds(self, namespace=namespace, class_=class_)

    def generate(self,db=None,reset=True):
        
        if db==None:
            db=self.db

        path_server = self.config.data["path"]+"/server/"
        
        if path_server not in sys.path:
            sys.path.append(path_server)

        j.sal.fs.touch(path_server+"__init__.py")

        #copy the templates in the local server dir
        for item in ["system"]:
            dest = path_server+"%s.py"%item
            if reset or not j.sal.fs.exists(dest):
                src = j.servers.gedis._path+"/templates/%s.py"%item
                j.sal.fs.copyFile(src,dest)

        for namespace,table in db.tables.items():
            url = table.schema.url.replace(".","_")
            dest = path_server+"model_%s.py"%url
            if reset or not j.sal.fs.exists(dest):
                code = j.servers.gedis.code_model_template.render(obj= table.schema)
                j.sal.fs.writeFile(dest,code)

        # j.sal.fs.listFilesInDir()
