from logging import getLogger
from js9 import j
from redis.connection import (ConnectionError, Encoder, PythonParser,
                              SocketBuffer)

logger = getLogger(__name__)


class CommandParser(PythonParser):
    """Parse the command send from the client"""

    def __init__(self, socket, socket_read_size=8192):
        super(CommandParser, self).__init__(socket_read_size=socket_read_size)
        self._sock = socket
        self._buffer = SocketBuffer(self._sock, self.socket_read_size)
        self.encoder = Encoder(encoding='utf-8', encoding_errors='strict', decode_responses=False)

    def read_request(self):
        # rename the function to map more with server side
        return self.read_response()


class ResponseWriter(object):
    """Writes data back to client as dictated by the Redis Protocol."""

    def __init__(self, socket):
        self.socket = socket
        self.dirty = False
        self.encoder = Encoder(encoding='utf-8', encoding_errors='strict', decode_responses=False)

    def encode(self, value):
        """Respond with data."""
        # data = self.encoder.encode(value)
        # self._write(data)
        # data = self.encoder.encode(value)
        # self._write(data)
        # if isinstance(value, (list, tuple)):
        #     self._write('*%d\r\n' % len(value))
        #     for v in value:
        #         self._bulk(v)
        if isinstance(value, int):
            self._write(':%d\r\n' % value)
        elif isinstance(value, bool):
            self._write(':%d\r\n' % (1 if value else 0))
        elif isinstance(value, str):
            self._bulk(value)
        elif isinstance(value, bytes):
            self._bulkbytes(value)
        else:
            value = j.data.serializer.json.dumps(value)
            self._bulk(value)


    def status(self, msg="OK"):
        """Send a status."""
        self._write("+%s\r\n" % msg)

    def error(self, msg):
        """Send an error."""
        data = ['-', str(msg), "\r\n"]
        self._write("".join(data))

    def _bulk(self, value):
        """Send part of a multiline reply."""
        data = ["$", str(len(value)), "\r\n", value, "\r\n"]
        self._write("".join(data))

    def _bulkbytes(self, value):
        data = [b"$", str(len(value)).encode(), b"\r\n", value, b"\r\n"]
        self._write(b"".join(data))

    def _write(self, data):
        if not self.dirty:
            self.dirty = True

        if isinstance(data, str):
            data = data.encode()
        # print("SENDING {} {} on wire".format(data, type(data)))
        self.socket.sendall(data)
