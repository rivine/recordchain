
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
namespace = ""
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

        self.cmds_meta = {}
        self.classes = {}
        self.cmds = {}

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

    def __handle_connection(self, socket, address):
        self.logger.info('connection from {}'.format(address))
        parser = CommandParser(socket)
        response = ResponseWriter(socket)

        try:
            while True:
                request = parser.read_request()
                cmd = request[0]
                redis_cmd = cmd.decode("utf-8").lower()

                cmd , err = self.method_get(redis_cmd)
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
                        from IPython import embed;embed(colors='Linux')
                        s
                        response.error("more than 1 argument given, needs to be binary capnp message or json")
                        continue 
                    o=cmd.schema_in.get(capnpbin=request[1])
                    params=o.ddict
                    params.pop("id")
                    if cmd.schema_out:
                        params["schema_out"] = cmd.schema_out
                else:
                    if len(request) > 2:
                        params = request[1:]
                    else:
                        #no arguments just execute
                        params = None

                # execute command callback
                print("execute command callback")
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
                    response.error(msg)
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

    def start(self):
        self.logger.info("init server")
        j.logger.enabled = False
        self._logger = None

        self._sig_handler.append(gevent.signal(signal.SIGINT, self.stop))

        self.logger.info("start server")

        # add the cmds to the server
        path_server = self.config.data["path"]+"/server/"
        for item in j.sal.fs.listFilesInDir(path_server,filter="*.py",exclude=["__*"]):
            namespace_base = self.config.data["namespace"]
            if not namespace_base:
                raise RuntimeError("namespace cannot be empty")
            if namespace_base[-1] is not ".":
                namespace_base+="."                
            namespace = namespace_base+j.sal.fs.getBaseName(item)[:-3].lower()
            self.cmds_add(namespace, path=item)


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

        if path is not None:
            classname = j.sal.fs.getBaseName(path).split(".", 1)[0]
            dname = j.sal.fs.getDirName(path)
            if dname not in sys.path:
                sys.path.append(dname)

            exec("from %s import %s" % (classname, classname))
            class_ = eval(classname)

        self.cmds_meta[namespace] = GedisCmds(self, namespace=namespace, class_=class_)
        # self.classes[namespace] =class_()

    def generate(self,db=None,reset=False):
        
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
                src = j.servers.gedis2._path+"/templates/%s.py"%item
                j.sal.fs.copyFile(src,dest)

        for namespace,table in db.tables.items():
            # url = table.schema.url.replace(".","_")
            dest = path_server+"model_%s.py"%namespace
            # table.schema.url_ = url
            if reset or not j.sal.fs.exists(dest):
                code = j.servers.gedis2.code_model_template.render(obj= table.schema)
                j.sal.fs.writeFile(dest,code)

    @property
    def namespace(self):
        return self.config.data["namespace"]

    def method_get(self,cmd):

        if cmd in self.cmds:
            return (self.cmds[cmd],"")

        print("* method miss:%s"%cmd)
        
        pre,post=cmd.split(".",1)

        namespace=self.namespace+"."+pre
        

        # if namespace not in self.classes:
        #     return (None,"Cannot find class with name:%s in namespace:%s"%(pre,namespace))
        # cl=self.classes[pre]

        if namespace not in self.cmds_meta:
            return (None,"Cannot find namespace:%s"%(namespace))

        meta = self.cmds_meta[namespace]

        # meta.cmds
        # print(meta.cmds)

        if not post in meta.cmds:
            return (None,"Cannot find method with name:%s in namespace:%s"%(post,namespace))
        
        cmd_obj = meta.cmds[post]

        try:
            # m = eval("cl.%s"%(post))
            m = cmd_obj.method
        except Exception as e:
            return (None,"Could not execute code of method '%s' in namespace '%s'\n%s"%(pre,namespace,e))

        #we need to do this, to make sure that the code could be interpreted, now we now method is ok
        self.cmds[cmd] = cmd_obj

        return (self.cmds[cmd],"")
