
from js9 import j
import signal

import gevent.signal
from gevent.pool import Pool
from gevent.server import StreamServer
from .protocol import CommandParser, ResponseWriter

JSBASE = j.application.jsbase_get_class()

class RedisServer(StreamServer, JSBASE):

    def __init__(self, host='0.0.0.0', port=6380, keyfile="/etc/ssl/private/server.key", certfile="/etc/ssl/certs/server.crt"):
        JSBASE.__init__(self)
        self._server = StreamServer(
            (host, port), spawn=Pool(), handle=self.__handle_connection, keyfile=keyfile, certfile=certfile)
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
                    self.logger.debug( "Callback done and result {} , type {}".format(result, type(result)) )
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
        j.logger.enabled = False
        self._logger=None
    
        for item in self.__dir__():
            # self.logger.debug("method:%s"%item)
            if item.endswith("_cmd"):
                item2=item[:-4]
                #found a method which is a command
                cmd = eval("self.%s"%item)
                self.register_command(item2,cmd)

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
