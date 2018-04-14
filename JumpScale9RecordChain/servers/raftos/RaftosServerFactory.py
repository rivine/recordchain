
from pprint import pprint as print

from js9 import j

import sys
sys.path.append("%s/github/rivine/recordchain/JumpScale9RecordChain/servers/raftos"%j.dirs.CODEDIR)


from .RaftosServer import RaftosServer
from .RaftosCluster import RaftosCluster


JSConfigBase = j.tools.configmanager.base_class_configs

class RaftosServerFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.servers.raftos_server"
        super(RaftosServerFactory, self).__init__(RaftosCluster)



    def get_by_params(self, instance="main", secret="1233", members = "localhost:4441,localhost:4442,localhost:4443", cmd="j.servers.raftos_server.example_server_class_get()"):

        data = {}
        data["secret_"] = secret
        data["members"] = members
        data ["cmd"] = cmd
        return self.get(instance=instance, data=data, create=True)


    def example_server_class_get(self):
        return RaftosServer

    def start_local(self,nrservers=3,startport=4000,cmd="j.servers.raftos_server.example_server_class_get()" ):
        """
        start local cluster of 5 nodes, will be run in tmux
        """
        members=""
        for i in range(nrservers):
            members+="127.0.0.1:%s,"%(startport+i)

        members=members.rstrip(",")

        cluster = self.get_by_params( instance="main", secret="1233", members=members, cmd=cmd)
        cluster.start(background=True)


    def test(self):
        """
        js9 'j.servers.raftos_server.test()'
        """
        self.start_local(nrservers=3,startport=7000,cmd="j.servers.raftos_server.example_server_class_get()")

