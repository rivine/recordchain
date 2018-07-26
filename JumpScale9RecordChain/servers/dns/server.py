
from js9 import j
import signal
import dnslib

# import gevent.signal
# from gevent.pool import Pool
from gevent.server import DatagramServer
from gevent import monkey
monkey.patch_all()
# from .protocol import CommandParser, ResponseWriter

JSBASE = j.application.jsbase_get_class()

soaexample = dnslib.SOA(
    mname="ns1.example.com",  # primary name server
    rname="info.example.com",  # email of the domain administrator
    times=(
        201307231,  # serial number
        60 * 60 * 1,  # refresh
        60 * 60 * 3,  # retry
        60 * 60 * 24,  # expire
        60 * 60 * 1,  # minimum
    )
)

#see https://github.com/andreif/dnslib  for more info how to use the lib

class DNSServer(DatagramServer, JSBASE):

    def __init__(self,port=53):
        JSBASE.__init__(self)
        DatagramServer.__init__(self,":%s"%port,handle=self.handle)
        self.TTL = 60 * 5

        self.rtypes = {}
        self.rtypes["A"] = dnslib.QTYPE.A
        self.rtypes["AAAA"] = dnslib.QTYPE.AAAA
        self.rtypes["NS"] = dnslib.QTYPE.NS
        self.rtypes["MX"] = dnslib.QTYPE.MX

        self.rdatatypes = {}
        self.rdatatypes["A"] = dnslib.A
        self.rdatatypes["AAAA"] = dnslib.AAAA
        self.rdatatypes["NS"] = dnslib.NS
        self.rdatatypes["MX"] = dnslib.MX
        
        # self.db = j.clients.redis.core_get()

    def start(self):
        self.serve_forever()


    def handle(self, data, address):
        # self.logger.debug('%s: got %r' % (address[0], data))
        if data==b"PING":
            self.sendback(b"PONG", address)
        else:
            # self.sendback(b"ERROR", address)
            # print len(data), data.encode('hex')
            resp = self.dns_response(data)
            self.sendback(resp, address)


    def sendback(self,data,address):
        try:
            self.socket.sendto(data, address)
        except Exception as e:
            self.logger.error("error in communication:%s"%e)


    def resolve(self,qname,type="A"):
        def do(qname,type):
            name =  str(qname).rstrip(".")
            if name.split(".")[-1].upper() in j.servers.dns.dns_extensions:
                res = []
                try:
                    resp = j.tools.dnstools.default.resolver.query(name,type)
                except Exception as e:
                    if "NoAnswer" in str(e):
                        self.logger.warning("did not find:%s"%qname)
                        return []
                    self.logger.error("could not resolve:%s (%s)"%(e,qname))
                    return []
                for rr in resp:
                    if type == "A":
                        res.append( rr.address)
                    elif type == "AAAA":
                        self.logger.debug("AAAA")
                        res.append( rr.address)
                    else:
                        res.append(str(rr.target))

                return res
            else:
                if type == "NS":
                    return ["127.0.0.1"]
                else:
                    return ["192.168.1.1"]
                #TODO: need to get DNS records from a source
        
        res = self.cache.get(key="resolve_%s_%s"%(qname,type),method=do,expire=600, qname=qname,type=type)
        self.cache.reset() #basically don't use cache, just for debugging later should disable this line
        return res

    def dns_response(self,data):
        
        request = dnslib.DNSRecord.parse(data)

        self.logger.debug ("request:%s"%request)

        reply = dnslib.DNSRecord(dnslib.DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)

        qname = request.q.qname
        qn = str(qname)
        qtype = request.q.qtype
        qt = dnslib.QTYPE[qtype]

        addrs = self.resolve(qname,qt)

        if qt in ["A","MX","NS","AAAA"]:
            for item in addrs:
                reply.add_answer(dnslib.RR(rname=qname, rtype=self.rtypes[qt], rclass=1, ttl=self.TTL, rdata=self.rdatatypes[qt](item)))
                self.logger.debug("DNS reply:%s:%s"%(qt,reply))
        else:
            #TODO:*1 add the other record types e.g. SOA & txt & ...
            self.logger.error("did not find type:\n%s"%request)
        

        return reply.pack()
