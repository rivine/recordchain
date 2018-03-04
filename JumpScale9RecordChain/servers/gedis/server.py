from logging import getLogger
import signal

import gevent.signal
from gevent.pool import Pool
from gevent.server import StreamServer

from .protocol import CommandParser, ResponseWriter


logger = getLogger(__name__)


class RedisServer(StreamServer):

    def __init__(self, host='0.0.0.0', port=6379):
        self._server = StreamServer((host, port), spawn=Pool(), handle=self.__handle_connection)
        self._sig_handler = []
        # commands callbacks
        self._cmds = {}

    def register_command(self, cmd, callback):
        if isinstance(cmd, str):
            cmd = cmd.encode('utf-8')
        self._cmds[cmd] = callback

    def __handle_connection(self, socket, address):
        logger.info('connection from %s', address)
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
                self._cmds[cmd](request, response)

        except ConnectionError as err:
            logger.info('connection error: %s', str(err))
        finally:
            parser.on_disconnect()
            logger.info('close connection from %s', address)

    def start(self):
        logger.info("start server")
        self._sig_handler.append(gevent.signal(signal.SIGINT, self.stop))

        self._server.serve_forever()

    def stop(self):
        """
        stop receiving requests and close the server
        """
        # prevent the signal handler to be called again if
        # more signal are received
        for h in self._sig_handler:
            h.cancel()

        logger.info('stopping server')
        self._server.stop()
