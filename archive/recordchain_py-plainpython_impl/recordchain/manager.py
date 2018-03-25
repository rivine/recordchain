from pickle import dump, load
from .chain import Blockchain, Transaction, InvalidBlockchainException, InvalidBlockException, uniq_id, DB0
from .apptypes import *
from merkletools import MerkleTools



# TRANSACTIONS OR ACTIONS ALLOWED IN THE APPLICATION. 
TRANSACTIONS = ["add-bdomain", "update-bdomain", "delete-bdomain", 
                "add-bobject", "update-bobject", "delete-bobject"
                "add-group", "update-group", "delete-group",
                "add-user", "update-user", "delete-user",
                "add-acl", "update-acl", "delete-acl",
                "add-aci", "update-aci", "delete-aci",
]


class ACTION_DATA:
    def __init__(self, **kwargs):
        """
        Wraps the transaction data in a hashable object.
        # TODO complexity can be reduced to a simple function
        """
        self.data = kwargs

    @property
    def hash(self):
        return hash(str(self.data.items()))


class Manager:

    def __init__(self):

        """
    Application controller
        we have 2 separate chains for bdomains and bobjects.
        and for the current application state we maintain 
            db0domains for bdomains state: dict of domain uid -> bdomain.
            db0objects for bobjects state: dict of object uid -> bobject.
            users for users state: user_id -> user_dict
            groups for groups state: group_id -> group_dict 
            acls for acls state: acl_id -> acl_dict 
            acis for acis state: aci_id -> aci_dict

    Trying to follow tendermint application pattern to have check_tx, deliver_tx
        for every action we have make_action_name_tx and check_action_name_tx and 

        make_action_name_tx method should wrap action data into suitable transaction format.
    ```    
    def make_add_bdomain_tx(self, **kwargs):
        t = Transaction("add-bdomain", ACTION_DATA(**kwargs))
        return t
    ```

    and check_action_name_tx should have the logic to check the validity of the action
    for instance deleting bobject transaction while the bobjcet doesn't exist.

    ```
        def check_delete_bobject_tx(self, tx):
            domuid = tx.tdata.data['uid']
            return self.db0objects.get(domuid, False) 
    ```

    and dispatching the transaction to the manager using `handle_tx` method 
```
    m = Manager()
    tx_add1 = m.make_add_bdomain_tx(name="codescalers.egypt")
    tx_add2 = m.make_add_bdomain_tx(name="gig.uk")
    tx_add3 = m.make_add_bdomain_tx(name="gig.be")
    m.handle_tx(tx_add1)
    m.handle_tx(tx_add2)
    m.handle_tx(tx_add3)

    assert m.bdomainschain.tx_count == 3
    print(m.bdomainschain)
```
        """

        # We have to chains 1 for bdomains and 1 for bobjects.
        self.bdomainschain = Blockchain()
        self.bobjectschain = Blockchain()

        # NOT utilized yet.
        self.bdomainstree = MerkleTools(hash_type="md5")
        self.bobjectstree = MerkleTools(hash_type="md5")

        ## QUESTION: IS THIS THE CORRECT WAY TO REPRESENT THE STATE?
        self.db0domains = DB0()
        self.db0objects = DB0()
        self.users = DB0()
        self.groups = DB0()
        self.acls = DB0()
        self.acis = DB0() 

        self.revtable = {}  #type_uid : bobject_uid
    
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
                self.bdomainschain.add_transaction(tx)
                print("CREATE TRANSACTION ADDED SUCCESSFULLY")
        elif tx.ttype == "delete-bdomain":
            b = self.check_delete_bdomain_tx(tx)
            if b:
                self.bdomainschain.add_transaction(tx)
                del self.db0domains[tx.tdata.data['uid']]
                print("DELETE TRANSACTION ADDED SUCCESSFULLY")
        elif tx.ttype == "update-bdomain":
            b = self.check_update_bdomain_tx(tx)
            if b:
                for k,v in tx.tdata.data.items():
                    setattr(b, k, v)
                self.db0domains.update(b.uid, tx.tdata.data)
                self.bdomainschain.add_transaction(tx)
                print("UPDATE TRANSACTION ADDED SUCCESSFULLY")

    def _handle_bobject_add_tx(self, tx):
        txdata = tx.tdata.data
        b = self.check_add_bobject_tx(tx)
        if b:
            b.uid = self.db0objects.incid + 1
            txdata['uid'] = b.uid
            self.db0objects.set(b.uid, txdata)
            self.bobjectschain.add_transaction(tx)
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
            self.bobjectschain.add_transaction(tx)
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
            self.bobjectschain.add_transaction(tx)
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

    def save_chains(self, filepath):
        """Save chain to a file"""
        chains = {'bdomainschain': self.bdomainschain, 'bobjectschain':self.bobjectschain}
        with open(filepath, "wb") as f:
            dump(chains, f)

    def load_chains(self, filepath):
        """Load chain from a file"""
        with open(filepath, "rb") as f:
            chains = load(f)
            self.bobjectschain = chains['bobjectschain']
            self.bdomainschain = chains['bdomainschain']


    def reset_chains(self):
        """
        reset the state of the application.
        """
        self.bdomainschain = Blockchain()
        self.bobjectschain = Blockchain()
        self.bdomainstree = MerkleTools(hash_type="md5")
        self.bobjectstree = MerkleTools(hash_type="md5")
        self.db0domains = DB0()
        self.db0objects = DB0()
        self.users = {}
        self.groups = {}
        self.acls = {}
        self.acis = {}


    def restore_state(self):
        """
        Apply the transactions from the chains the achieve the application state.
        """
        for tx in self.bdomainschain:
            self.handle_tx(tx)
        for tx in self.bobjectschain:
            self.handle_tx(tx)
