
from js9 import j
import signal

import gevent.signal
from gevent.pool import Pool
from gevent.server import StreamServer
from .protocol import CommandParser, ResponseWriter

JSBASE = j.application.jsbase_get_class()

basemethods=['_logger',
 '_cache',
 '_cache_expiration',
 '_logger_force',
 '_server',
 '_sig_handler',
 '_cmds',
 '___name__',
 '__module__',
 '__init__',
 'register_command',
 '_RedisServer__handle_connection',
 'start',
 'stop',
 '__doc__',
 'backlog',
 'reuse_addr',
 'ssl_enabled',
 'set_listener',
 'init_socket',
 'get_listener',
 'do_read',
 'do_close',
 'wrap_socket_and_handle',
 'min_delay',
 'max_delay',
 'max_accept',
 '_spawn',
 'stop_timeout',
 'fatal_errors',
 'set_spawn',
 'set_handle',
 '_start_accepting_if_started',
 'start_accepting',
 'stop_accepting',
 'do_handle',
 '_do_read',
 'full',
 '__repr__',
 '__str__',
 '_formatinfo',
 'server_host',
 'server_port',
 'started',
 'close',
 'closed',
 'serve_forever',
 'is_fatal_error',
 '__dict__',
 '__weakref__',
 '__hash__',
 '__getattribute__',
 '__setattr__',
 '__delattr__',
 '__lt__',
 '__le__',
 '__eq__',
 '__ne__',
 '__gt__',
 '__ge__',
 '__new__',
 '__reduce_ex__',
 '__reduce__',
 '__subclasshook__',
 '__init_subclass__',
 '__format__',
 '__sizeof__',
 '__dir__',
 '__class__',
 '__name__',
 'logger',
 'logger_enable',
 'cache']

class RedisServer(StreamServer, JSBASE):

    def __init__(self, host='0.0.0.0', port=6379):
        JSBASE.__init__(self)
        self._server = StreamServer(
            (host, port), spawn=Pool(), handle=self.__handle_connection)
        self._sig_handler = []
        # commands callbacks
        self._cmds = {}

    def register_command(self, cmd, callback):
        self.logger.info("add cmd %s"%cmd)
        if isinstance(cmd, str):
            cmd = cmd.encode('utf-8')
            cmd = cmd.upper()
        self._cmds[cmd] = callback

    def __handle_connection(self, socket, address):
        self.logger.info('connection from {}'.format(address))
        parser = CommandParser(socket)
        response = ResponseWriter(socket)

        try:
            while True:
                request = parser.read_request()
                cmd = request[0]
                if cmd not in self._cmds:
                    response.error('command not supported')
                    continue

                # execute command callback
                result = ""
                try:
                    result = self._cmds[cmd](request)
                    self.logger.info( "Callback done and result {} , type {}".format(result, type(result)) )
                except Exception as e:
                    print("exception in redis server")
                    eco = j.errorhandler.parsePythonExceptionObject(e)
                    response.error(str(eco))
                    continue
                self.logger.debug("response:{}:{}:{}".format(address,cmd,result))
                response.encode(result)

        except ConnectionError as err:
            self.logger.info('connection error: {}'.format(str(err)))
        finally:
            parser.on_disconnect()
            self.logger.info('close connection from {}'.format(address))

    def start(self):
        self.logger.info("init server")

        for item in self.__dir__():
            # self.logger.debug("method:%s"%item)
            if item not in basemethods:
                #found a method which is a command
                cmd = eval("self.%s"%item)
                self.register_command(item,cmd)

        self._sig_handler.append(gevent.signal(signal.SIGINT, self.stop))
        
        self.logger.info("start server")
        self._server.serve_forever()

    def stop(self):
        """
        stop receiving requests and close the server
        """
        # prevent the signal handler to be called again if
        # more signal are received
        for h in self._sig_handler:
            h.cancel()

        self.logger.info('stopping server')
        self._server.stop()
