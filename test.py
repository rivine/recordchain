from js9 import j

p = j.tools.prefab.local
p.runtimes.pip.install("dnslib,nltk,nameparser,gevent,unidecode")

j.servers.zdb.test(build=True)
j.data.indexfile.test()
j.data.schema.test()

j.data.bcdb.test()
j.data.indexdb.test()

if p.platformtype.isLinux:

    j.servers.dns.test()