
from pprint import pprint as print

from js9 import j

from .server import DNSServer
import os
JSBASE = j.application.jsbase_get_class()
from gevent import socket

#http://mirror1.malwaredomains.com/files/justdomains  domains we should not query, lets download & put in redis core
#https://blog.cryptoaustralia.org.au/2017/12/05/build-your-private-dns-server/

class DNSServerFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.servers.dns"
        JSBASE.__init__(self)
        self._extensions = {}

    def get(self,port=53):
        return DNSServer(port=port)

    def start(self,port=53,background=False):
        """
        js9 'j.servers.dns.start()'
        """
        if background:
            if j.core.platformtype.myplatform.isMac and port<1025:
                print("PLEASE GO TO TMUX SESSION, GIVE IN PASSWD FOR SUDO, do tmux a")
                cmd = "sudo js9 'j.servers.dns.start(background=False,port=%s)'"%port
            else:
                cmd = "js9 'j.servers.dns.start(background=False,port=%s)'"%port
            j.tools.tmux.execute(cmd, session='main', window='dnsserver',pane='main', session_reset=False, window_reset=True)
            self.logger.info("waiting for uidserver to start on port %s"%port)
            res = j.sal.nettools.waitConnectionTest("localhost",port)
        else:
            s = self.get(port=port)
            s.start()

    
    @property
    def dns_extensions(self):
        """
        all known extensions on http://data.iana.org/TLD/tlds-alpha-by-domain.txt
        """
        if self._extensions=={}:
            path = os.path.join(os.path.dirname(__file__), "knownextensions.txt")
            for line in j.sal.fs.readFile(path).split("\n"):
                if line.strip()=="" or line[0]=="#":
                    continue
                self._extensions[line]=True
        return self._extensions

    def ping(self,addr='localhost',port=53):
        """
        js9 'print(j.servers.dns.ping(port=53))'
        """
        
        address = (addr, port)
        message = b'PING'
        sock = socket.socket(type=socket.SOCK_DGRAM)
        sock.connect(address)
        print ('Sending %s bytes to %s:%s' % ((len(message), ) + address))
        sock.send(message)
        try:
            data, address = sock.recvfrom(8192)
        except Exception as e:
            if "refused" in str(e):
                return False
            raise RuntimeError("unexpected result")
        return True


    def test(self,start=False,port=5354):
        """
        js9 'j.servers.dns.test()'
        """        

        if start or not self.ping(port=port):
            self.start(background=True,port=port)

        def ping():
            from gevent import socket
            address = ('localhost', port)
            message = b'PING'
            sock = socket.socket(type=socket.SOCK_DGRAM)
            sock.connect(address)
            print ('Sending %s bytes to %s:%s' % ((len(message), ) + address))
            sock.send(message)
            data, address = sock.recvfrom(8192)
            print ('%s:%s: got %r' % (address + (data, )))
            assert data == b"PONG"

        ping()

        ns = j.tools.dnstools.get(["localhost"],port=port)

        print(ns.namerecords_get("google.com"))
        print(ns.namerecords_get("info.despiegk"))

