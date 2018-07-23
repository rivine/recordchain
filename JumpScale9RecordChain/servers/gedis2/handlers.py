from js9 import j

from redis.exceptions import ConnectionError
from geventwebsocket.exceptions import WebSocketError
from .protocol import RedisResponseWriter, RedisCommandParser, WebsocketResponseWriter, WebsocketsCommandParser

JSBASE = j.application.jsbase_get_class()


class Handler(JSBASE):
    def __init__(self, instance, cmds, classes, cmds_meta):
        JSBASE.__init__(self)
        self.cmds = cmds
        self.classes = classes
        self.instance = instance
        self.cmds_meta = cmds_meta

    def _handle_request(self, socket, address):
        self.logger.info('connection from {}'.format(address))
        self.parser = self.get_parser(socket)
        self.response = self.get_response(socket)

        while True:
            request = self.parser.read_request()

            if request is None:
                break

            if not request:  # empty list request
                # self.response.error('Empty request body .. probably this is a (TCP port) checking query')
                continue

            cmd = request[0]
            redis_cmd = cmd.decode("utf-8").lower()

            cmd, err = self.get_command(redis_cmd)
            if err is not "":
                self.response.error(err)
                continue
            if cmd.schema_in:
                if len(request) < 2:
                    self.response.error("need to have arguments, none given")
                    continue
                if len(request) > 2:
                    cmd.schema_in.properties
                    print("more than 1 input")
                    self.response.error("more than 1 argument given, needs to be binary capnp message or json")
                    continue

                try:
                    # Try capnp
                    id, data = j.data.serializer.msgpack.loads(request[1])
                    o = cmd.schema_in.get(capnpbin=data)
                    if id:
                        o.id = id
                except:
                    # Try Json
                    o = cmd.schema_in.get(data=j.data.serializer.json.loads(request[1]))

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

            self.logger.debug("execute command callback:%s:%s" % (cmd, params))
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
                msg += "\nCODE:%s:%s\n" % (cmd.namespace, cmd.name)
                print (msg)
                import ipdb; ipdb.set_trace()
                self.response.error(e.args[0])
                continue
            self.logger.debug(
                "response:{}:{}:{}".format(address, cmd, result))

            if cmd.schema_out:
                result = self.encode_result(result)
            self.response.encode(result)

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

    def handle(self, socket, address):
        """
        handle request
        :return:
        """
        raise NotImplementedError()

    def encode_result(self, result):
        """
        Get data format to be sent to client
        ie capnp or json according to Handler type used
        """
        raise NotImplementedError()

    def encode_error(self, err):
        """
        Get error format to be sent to client
        """
        raise NotImplementedError()

    def get_parser(self, socket):
        raise NotImplementedError()

    def get_response(self, socket):
        raise NotImplementedError()


class RedisRequestHandler(Handler):
    def handle(self, socket, address):
        try:
            self._handle_request(socket, address)
        except ConnectionError as err:
            self.logger.info('connection error: {}'.format(str(err)))
        finally:
            self.parser.on_disconnect()
            self.logger.info('close connection from {}'.format(address))

    def encode_result(self, result):
        return result.data

    def encode_error(self, error):
        return error

    def get_parser(self, socket):
        return RedisCommandParser(socket)

    def get_response(self, socket):
        return RedisResponseWriter(socket)


class WebsocketRequestHandler(Handler):
    def handle(self, socket, address):
        try:
            self._handle_request(socket, address)
        except WebSocketError as err:
            self.logger.info('connection error: {}'.format(str(err)))
        finally:
            self.logger.info('close connection from {}'.format(address))

    def encode_result(self, result):
        return result.ddict_hr

    def encode_error(self, error):
        return error.encode('utf-8')

    def get_parser(self, socket):
        return WebsocketsCommandParser(socket)

    def get_response(self, socket):
        return WebsocketResponseWriter(socket)
