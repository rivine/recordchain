
from js9 import j

import time

JSBASE = j.application.jsbase_get_class()

import raftos_ as raftos
import asyncio
import random
from datetime import datetime

async def run(node_id):
    # Any replicated object with get/set functions
    data_id = raftos.Replicated(name='data_id')

    # Dict-like object: data.update(), data['key'] etc
    data = raftos.ReplicatedDict(name='data')

    # List-like object: data_list.append(), data_list[-1]
    data_list = raftos.ReplicatedList(name='data_list')

    while True:
        # We can also check if raftos.get_leader() == node_id

        # await raftos.wait_until_leader(node_id)
        if raftos.get_leader() == node_id:
            print("leader ok")

            await asyncio.sleep(2)

            current_id = random.randint(1, 1000)
            data_map = {
                str(current_id): {
                    'created_at': datetime.now().strftime('%d/%m/%y %H:%M')
                }
            }

            print("data id set")
            await data_id.set(current_id)
            print("data update")
            await data.update(data_map)
            print("data list append")
            await data_list.append(data_map)

            print(data)

            from IPython import embed;embed(colors='Linux')

        await asyncio.sleep(2)
        

class RaftosServer(JSBASE):

    def __init__(self, port, members, secret=""):
        JSBASE.__init__(self)

        self._members = members
        self.port = port

        self.remotes = ["%s:%s" % item for item in self.members]
        self.local = "127.0.0.1:%s"%(self.port)
    
        self.logger.debug("me:"+self.local)
        self.logger.debug("members:%s"%self.remotes)
        # self.logger.debug("secret:%s"%secret)

        self.start()


    @property
    def members(self):
        res = []
        for item in self._members.split(","):
            addr, port = item.split(":")
            addr = addr.strip()
            port = int(port)
            res.append((addr, port))
        return res

    def start(self):
        
        raftos.configure({
            'log_path': './',
            'serializer': raftos.serializers.JSONSerializer
        })

        loop = asyncio.get_event_loop()
        loop.create_task(raftos.register(self.local, cluster=self.remotes))
        loop.run_until_complete(run(self.local))
            