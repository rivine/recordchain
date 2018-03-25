
from pprint import pprint as print

from js9 import j

from .server import DNSServer
import os
JSBASE = j.application.jsbase_get_class()


#http://mirror1.malwaredomains.com/files/justdomains  domains we should not query, lets download & put in redis core
#https://blog.cryptoaustralia.org.au/2017/12/05/build-your-private-dns-server/

class DNSServerFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.servers.dns"
        JSBASE.__init__(self)
        self._extensions = {}

    def get(self):
        return DNSServer()

    def start(self,background=False):
        """
        js9 'j.servers.dns.start()'
        """
        if background:
            if j.core.platformtype.myplatform.isMac:
                cmd = "sudo js9 'j.servers.dns.start(background=False)'"
            else:
                cmd = "js9 'j.servers.dns.start(background=False)'"
            j.tools.tmux.execute(cmd, session='main', window='dnsserver',pane='main', session_reset=False, window_reset=True)
            self.logger.info("waiting for uidserver to start on port 53")
            res = j.sal.nettools.waitConnectionTest("localhost",53)
        else:
            s = self.get()

    
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


    def test(self,start=False):
        """
        js9 'j.servers.dns.test()'
        """        

        if start:
            self.start()

        def ping():
            from gevent import socket
            address = ('localhost', 53)
            message = b'PING'
            sock = socket.socket(type=socket.SOCK_DGRAM)
            sock.connect(address)
            print ('Sending %s bytes to %s:%s' % ((len(message), ) + address))
            sock.send(message)
            data, address = sock.recvfrom(8192)
            print ('%s:%s: got %r' % (address + (data, )))
            assert data == b"PONG"

        ping()

        ns = j.tools.dnstools.get(["localhost"])

        print(ns.namerecords_get("test.test.com"))
        print(ns.nameservers_get())
        print(ns.namerecords_get("info.despiegk"))
        print(ns.nameservers_get("info.despiegk"))

