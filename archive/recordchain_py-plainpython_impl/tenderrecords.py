import struct
import abci.utils as util

from abci import (
    ABCIServer,
    BaseApplication,
    utils,
    ResponseInfo,
    ResponseQuery,
    Result
)
from recordchain.chain import Transaction
from recordchain.chain import DB0
from recordchain.apptypes import *

logger = utils.get_logger()
# Tx encoding/decoding


from binascii import hexlify, unhexlify
import pickle
from recordchain.manager import Manager
# Tx encoding/decoding

def decode_tx(tx):
    return pickle.loads(unhexlify(tx)) 

class SimpleRC(BaseApplication):
    """Simple RC manager app
    To run it:
    - make a clean new directory for tendermint
    - start this server: python tenderrecords.py
    - start tendermint: tendermint --home "apphomedir" node
 
    - The send transactions to the app:

    curl -s 'localhost:46657/broadcast_tx_commit?tx="80037d710028580500000074646174617101637265636f7264636861696e2e6d616e616765720a414354494f4e5f444154410a7102298171037d710458040000006461746171057d7106285809000000617574686f725f696471074b0158040000006e616d65710858040000006f626a33710968057d710a28580400000061646472710b581200000075736572312e757365722e6469676974616c710c5805000000616c696173710d5d710e58050000007573657231710f61580300000075696471104e75757362580900000074696d657374616d707111636461746574696d650a6461746574696d650a7112430a07e2011710012408c94e711385711452711558090000007369676e617475726571164e58050000007474797065711758080000006164642d75736572711858050000005f6861736871195800000000711a58020000006964711b4b00752e"'
    ...
    to see the latest count:
    curl http://localhost:46657/abci_query

    The way the app state is structured, you can also see the current state value
    in the tendermint console output."""

    def info(self):
        r = ResponseInfo()
        r.last_block_height = 0
        r.last_block_app_hash = b''
        return r

    def init_chain(self, v):
        """Set initial state on first run"""

        self.db0domains = DB0()
        self.db0objects = DB0()
        self.users = DB0()
        self.groups = DB0()
        self.acls = DB0()
        self.acis = DB0() 

        self.revtable = {}  #type_uid : bobject_uid
        self.txCount = 0

    def check_tx(self, tx):
        """ Validate the Tx before entry into the mempool """
        txdecoded = tx.decode()
        logger.info("CHECKING TX: " + txdecoded)
        txdict = decode_tx(txdecoded)

        tx = Transaction.from_dict(txdict)
        return Result.ok(log='thumbs up')

    def deliver_tx(self, tx):
        """ Mutate state if valid Tx """
        txdecoded = tx.decode()
        logger.info("CHECKING TX: " + txdecoded)
        txdict = decode_tx(txdecoded)
        tx = Transaction.from_dict(txdict)
        self.handle_tx(tx)
        self.txCount += 1
        return Result.ok(log="delivered eshta")

    def query(self, reqQuery):
        """Return the last tx count"""
        rq = ResponseQuery(code=0, key=b'fullstate', value=hexlify(pickle.dump(self.stats())))

        return rq

    def commit(self):
        logger.info("COMMITTING"+str(self.stats()))
        """Return the current encode state value to tendermint"""
        h = struct.pack('>Q', self.txCount)
        return Result.ok(data=h)


    
    def stats(self):
        return {
            'users': self.users,
            'groups': self.groups,
            'acls': self.acls,
            'acis': self.acis,
        }

    def check_add_bdomain_tx(self, tx):
        try:
            return BDomain(**tx.tdata.data)
        except:
            return False

    def make_add_bdomain_tx(self, **kwargs):
        t = Transaction("add-bdomain", ACTION_DATA(**kwargs))
        return t

    def check_delete_bdomain_tx(self, tx):
        domuid = tx.tdata.data['uid']
        return self.db0domains.get(domuid, False)

    def make_delete_bdomain_tx(self, **kwargs):
        t = Transaction("delete-bdomain", ACTION_DATA(**kwargs))
        return t

    def check_update_bdomain_tx(self, tx):
        domuid = tx.tdata.data['uid']
        domdata = self.db0domains.get(domuid, False)
        if domdata:
            return BDomain(domdata)

    def make_update_bdomain_tx(self, **kwargs):
        t = Transaction("update-bdomain", ACTION_DATA(**kwargs))
        return t

    def check_add_bobject_tx(self, tx):
        try:
            return BObject(**tx.tdata.data)
        except:
            return False

    def make_add_bobject_tx(self, **kwargs):
        t = Transaction("add-bobject", ACTION_DATA(**kwargs))
        return t


    def make_add_user_tx(self, **kwargs):
        t = Transaction("add-user", ACTION_DATA(**kwargs))
        return t

    def make_add_group_tx(self, **kwargs):
        t = Transaction("add-group", ACTION_DATA(**kwargs))
        return t

    def make_add_acl_tx(self, **kwargs):
        t = Transaction("add-acl", ACTION_DATA(**kwargs))
        return t

    def make_add_aci_tx(self, **kwargs):
        t = Transaction("add-aci", ACTION_DATA(**kwargs))
        return t

    def check_delete_bobject_tx(self, tx):
        objuid = tx.tdata.data['uid']
        return self.db0objects.get(objuid, False)

    def make_delete_user_tx(self, **kwargs):
        t = Transaction("delete-user", ACTION_DATA(**kwargs))
        return t

    def make_delete_group_tx(self, **kwargs):
        t = Transaction("delete-group", ACTION_DATA(**kwargs))
        return t

    def make_delete_acl_tx(self, **kwargs):
        t = Transaction("delete-acl", ACTION_DATA(**kwargs))
        return t

    def make_delete_aci_tx(self, **kwargs):
        t = Transaction("delete-aci", ACTION_DATA(**kwargs))
        return t

    def make_delete_bobject_tx(self, **kwargs):
        t = Transaction("delete-bobject", ACTION_DATA(**kwargs))
        return t

    def check_update_bobject_tx(self, tx):
        objuid = tx.tdata.data['uid']
        objdata = self.db0objects.get(objuid, False)
        try:
            return BObject(**objdata)
        except:
            return False

    def make_update_bobject_tx(self, **kwargs):
        t = Transaction("update-bobject", ACTION_DATA(**kwargs))
        return t

    def make_update_user_tx(self, **kwargs):
        t = Transaction("update-user", ACTION_DATA(**kwargs))
        return t

    def make_update_group_tx(self, **kwargs):
        t = Transaction("update-group", ACTION_DATA(**kwargs))
        return t

    def make_update_acl_tx(self, **kwargs):
        t = Transaction("update-acl", ACTION_DATA(**kwargs))
        return t

    def make_update_aci_tx(self, **kwargs):
        t = Transaction("update-aci", ACTION_DATA(**kwargs))
        return t


    def _handle_bdomain_tx(self, tx):
        txdata = tx.tdata.data
        if tx.ttype == "add-bdomain":
            b = self.check_add_bdomain_tx(tx)
            if b:
                b.uid = self.db0domains.incid + 1
                txdata['uid'] = b.uid
                self.db0domains.set(b.uid, tx.tdata.data)
                # self.bdomainschain.add_transaction(tx)
                print("CREATE TRANSACTION ADDED SUCCESSFULLY")
        elif tx.ttype == "delete-bdomain":
            b = self.check_delete_bdomain_tx(tx)
            if b:
                # self.bdomainschain.add_transaction(tx)
                del self.db0domains[tx.tdata.data['uid']]
                print("DELETE TRANSACTION ADDED SUCCESSFULLY")
        elif tx.ttype == "update-bdomain":
            b = self.check_update_bdomain_tx(tx)
            if b:
                for k,v in tx.tdata.data.items():
                    setattr(b, k, v)
                self.db0domains.update(b.uid, tx.tdata.data)
                # self.bdomainschain.add_transaction(tx)
                print("UPDATE TRANSACTION ADDED SUCCESSFULLY")

    def _handle_bobject_add_tx(self, tx):
        txdata = tx.tdata.data
        b = self.check_add_bobject_tx(tx)
        if b:
            b.uid = self.db0objects.incid + 1
            txdata['uid'] = b.uid
            self.db0objects.set(b.uid, txdata)
            # self.bobjectschain.add_transaction(tx)
            print("CREATE TRANSACTION ADDED SUCCESSFULLY")
            if tx.ttype == "add-user":
                userdata = txdata['data']
                userdata['uid'] = self.users.incid + 1
                self.users.set(userdata['uid'], userdata)
                self.revtable["user_{}".format(userdata['uid'])] = b.uid
            elif tx.ttype == "add-group":
                groupdata = txdata['data']
                groupdata['uid'] = self.groups.incid + 1
                self.groups.set(groupdata['uid'], groupdata)
                self.revtable["group_{}".format(txdata['uid'])] = b.uid
            elif tx.ttype == "add-acl":
                acldata = txdata['data']
                acldata['uid'] = self.acls.incid + 1
                self.acls.set(acldata['uid'], acldata)
                self.revtable["acl_{}".format(acldata['uid'])] = b.uid
            elif tx.ttype == "add-aci":
                acidata = txdata['data']
                acidata['uid'] = self.acis.incid + 1
                self.acis.set(acidata['uid'], acidata)
                self.revtable["aci_{}".format(acidata['uid'])] = b.uid
        
    def _handle_bobject_delete_tx(self, tx):
        txdata = tx.tdata.data
        b = self.check_delete_bobject_tx(tx)
        if b:
            # self.bobjectschain.add_transaction(tx)
            del self.db0objects[txdata['uid']]
            if tx.ttype == "delete-user":
                del self.users[txdata['data']['uid']]
            elif tx.ttype == "delete-group":
                del self.groups[txdata['data']['uid']]
            elif tx.ttype == "delete-acl":
                del self.acls[txdata['data']['uid']]
            elif tx.ttype == "delete-aci":
                del self.acis[txdata['data']['uid']]
            print("DELETE TRANSACTION ADDED SUCCESSFULLY")

    def _handle_bobject_update_tx(self, tx):
        txdata = tx.tdata.data
        b = self.check_update_bobject_tx(tx)
        if b:
            for k,v in txdata.items():
                setattr(b, k, v)
            self.db0objects.update(b.uid, b)
            # self.bobjectschain.add_transaction(tx)
            print("UPDATE TRANSACTION ADDED SUCCESSFULLY")
            if tx.ttype == "update-user":
                objid = b.data['uid']
                obj = self.users[objid]
                payload = b.data.items()
                for k,v in payload:
                    obj[k] = v
                    self.users.update(objid, obj)
            elif tx.ttype == "update-group":
                objid = b.data['uid']
                obj = self.groups[objid]
                payload = b.data.items()
                for k,v in payload:
                    obj[k] = v
                    self.groups.update(objid, obj)
            elif tx.ttype == "update-acl":
                objid = b.data['uid']
                obj = self.groups[objid]
                payload = b.data.items()
                for k,v in payload:
                    obj[k] = v
                    self.acls.update(objid, obj)
            elif tx.ttype == "update-aci":
                objid = b.data['uid']
                obj = self.groups[objid]
                payload = b.data.items()
                for k,v in payload:
                    obj[k] = v
                    self.acis.update(objid, obj)


    def handle_tx(self, tx):
        """Handle transaction tx"""
        b = None
        print("RECVD tx: ", tx)

        ## Always remember
        ## Transaction has data
        ## data can be a bobject (which may has data of user, group, acl, aci)
        txdata = tx.tdata.data
        if tx.ttype in ["add-bdomain", "delete-bdomain", "update-bdomain"]:
            self._handle_bdomain_tx(tx)
        elif tx.ttype in ["add-bobject", "add-user", "add-group", "add-acl", "add-aci"]:
            self._handle_bobject_add_tx(tx)
        elif tx.ttype in ["delete-bobject", "delete-user", "delete-group", "delete-acl", "delete-aci"]:
            self._handle_bobject_delete_tx(tx)
        elif  tx.ttype in ["update-bobject", "update-user", "update-group", "update-acl", "update-aci"]:
            self._handle_bobject_update_tx(tx)


    def summary(self):
        """
    Debugging purposes shows details and len of users, groups, acls, acis
        """
        print("#USERS:", len(self.users))
        print(self.users)
        print("#GROUPS:", len(self.groups))
        print(self.groups)
        print("#ACLS:", len(self.acls))
        print(self.acls)
        print("#ACIS: ", len(self.acis))
        print(self.acis)

    # def save_chains(self, filepath):
    #     """Save chain to a file"""
    #     chains = {'bdomainschain': self.bdomainschain, 'bobjectschain':self.bobjectschain}
    #     with open(filepath, "wb") as f:
    #         dump(chains, f)

    # def load_chains(self, filepath):
    #     """Load chain from a file"""
    #     with open(filepath, "rb") as f:
    #         chains = load(f)
    #         self.bobjectschain = chains['bobjectschain']
    #         self.bdomainschain = chains['bdomainschain']


    # def reset_chains(self):
    #     """
    #     reset the state of the application.
    #     """
    #     self.bdomainschain = Blockchain()
    #     self.bobjectschain = Blockchain()
    #     self.bdomainstree = MerkleTools(hash_type="md5")
    #     self.bobjectstree = MerkleTools(hash_type="md5")
    #     self.db0domains = DB0()
    #     self.db0objects = DB0()
    #     self.users = {}
    #     self.groups = {}
    #     self.acls = {}
    #     self.acis = {}


    # def restore_state(self):
    #     """
    #     Apply the transactions from the chains the achieve the application state.
    #     """
    #     for tx in self.bdomainschain:
    #         self.handle_tx(tx)
    #     for tx in self.bobjectschain:
    #         self.handle_tx(tx)


if __name__ == '__main__':
    app = ABCIServer(app=SimpleRC())
    app.run()