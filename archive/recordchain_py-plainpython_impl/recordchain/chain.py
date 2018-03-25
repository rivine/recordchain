import random
import string
from os.path import expanduser
import datetime
from hashlib import md5
from base64 import b64encode, b64decode
from copy import deepcopy
from Crypto.PublicKey import RSA 
from Crypto.Signature import PKCS1_v1_5 
from Crypto.Hash import SHA256 
from Crypto.Hash import SHA256
from binascii import hexlify, unhexlify
import pickle


def generate_keys(name):
    """
    Generate private, public keys

    returns privatekey, pubey, privatekey path, pubkey path
    """
    from os import chmod
    from Crypto.PublicKey import RSA

    key = RSA.generate(2048)
    priv = key.exportKey().decode()
    pub = key.publickey().exportKey().decode()
    with open("/tmp/{}".format(name), 'w') as content_file:
        chmod("/tmp/{}".format(name),0o600)
        content_file.write(priv)
    with open("/tmp/{}.pub".format(name), 'w') as content_file:
        content_file.writelines(pub)
    
    return priv, pub, "/tmp/{}".format(name), "/tmp/{}.pub".format(name) 


def sign(hash, key_path="~/.ssh/id_rsa"):
    """
    Sign a digest with private key.
    """
    with open(expanduser(key_path), "r") as f:
        private_key = RSA.importKey(f.read())
        signer = PKCS1_v1_5.new(private_key) 
        signature = signer.sign(hash)
        return b64encode(signature)


def verify(hash, signature, key_path="~/.ssh/ida_rsa"):
    """
    Verify a digest signed with signature with public key calcuated from private key in key_path
    """
    key = open(expanduser(key_path), "r").read()
    rsakey = RSA.importKey(key) 
    pubkey = key.publickey()
    return pubkey.verify(hash, b64decode(signature)) == True


def uniq_id(n=5):
    return "".join(random.choice(string.hexdigits) for x in range(n))


# USE set, update explicitly
class DB0(dict):
    def __init__(self, *args, **kwargs):
        """
        Simulates 0-db: returns incremental ID on insertion
        """
        super().__init__(*args, **kwargs)
        self.incid = 0

    def __setitem__(self, k, v):
        super().__setitem__(k, v)

    def update(self, k, v):
        """
        update key k to value v
        """
        self[k] = v 

    def set(self, k, v):
        """
        Set key k to value v.
        @returns incremened ID
        """
        self.incid += 1
        self.__setitem__(k, v)
        return self.incid

db0 = DB0()

class InvalidBlockException(Exception):
    pass

class InvalidBlockchainException(Exception):
    pass



class Block(object):
    def __init__(self, transactions=None, prev_hash=""):
        """
        Block is a list of transactions with value of prev_hash
        """
        self.id = 0
        self.timestamp = datetime.datetime.now()
        self.prev_hash = prev_hash
        self._hash = ""
        self.transactions = transactions


    def seal(self):
        self.timestamp = datetime.datetime.now()
        _hash = "{}{}{}{}".format(self.id, str(self.transactions), self.timestamp, self.prev_hash)
        self._hash = md5(_hash.encode()).hexdigest()

    def __str__(self):
        return """
ID:           {}
TIMESTAMP:    {}
PREV_HASH:    {}
HASH:         {}
TRANSACTIONS:
*****
{}
*****
    """.format(self.id, self.timestamp, self.prev_hash, self.hash, "\n\n".join(str(x) for x in self.transactions))

    @property
    def hash(self):
        if self._hash is None:
            return self._hash
        self.seal()
        return self._hash
            
class Transaction(object):

    def __init__(self, ttype, tdata=None):
        """
        the application unit of action, stored in a transactions lit in a block.
            actions can be: [add-update-delete]-bdomain, [add-update-delete]-bobjects, users, groups, acls, acis

        ttype: transaction type.
        tdata: transaction data. (hashable)

        """
        self.id = 0
        self.ttype = ttype 
        self.tdata = tdata
        self._hash = ""
        self.signature = None
        self.timestamp = datetime.datetime.now()

    @classmethod
    def from_dict(cls, d):
        ttype = d.get('ttype')
        t = cls(ttype)
        t.__dict__ = d
        return t

    def seal(self):
        """
        Sealing the transaction should be done directly before adding to a block.
        """
        _tohash = "{}:{}:{}:{}".format(self.id, self.ttype, self.timestamp, self.tdata.hash)
        encoded_tohash = _tohash.encode()
        self._hash = md5(encoded_tohash).hexdigest()
        digest = SHA256.new()
        digest.update(encoded_tohash)
        self.signature = sign(digest)

    @property
    def hash(self):
        if self._hash is None:
            return self._hash
        self.seal()
        return self._hash

    def __str__(self):
        return "type:{} hash:{}\n data:{}\nsignature: {}".format(self.ttype, self.tdata.data, self.hash, self.signature)

class Blockchain(object):
    def __init__(self):
        """
        Simple blockchain implementation 
        list of blocks: [Block] 
        """

        self.blocks = []
        self.tnx_per_block = 2

    def get_block_by_id(self, id):
        """Get block by id."""
        return deepcopy(self.blocks[id])


    def get_last_block(self):
        """Get the last block in the chain."""
        return self.blocks[-1]


    def add(self, block):
        """Add block to chain"""
        if not self.blocks:
            block.prev_hash = ""
        else:
            block.prev_hash = self.blocks[-1].hash
        block.id = len(self.blocks) + 1
        block.seal()
        self.blocks.append(block)
    
    @property
    def transactions(self):
        for b in self.blocks:
            for t in b.transactions:
                yield t 

    def add_transaction(self, tx):
        """Add transaction to a block. #TODO: make pending ones before commiting to a block.
                make sure to put the transaction inthe appropriate block depending on the tnx_per_block variable
                and if the block is genesis or not.
        
        """

        if self.blocks:
            last_block = self.blocks[-1]
            if len(last_block.transactions) >= self.tnx_per_block:
                b = Block(transactions=[tx], prev_hash=last_block.hash)
                self.add(b)
            else:
                self.blocks[-1].transactions.append(tx)
        else:
                b = Block(transactions=[tx], prev_hash="")
                self.add(b)
        
    def is_valid(self):
        """Check if a chain is valid or not."""
        for i, block in enumerate(self.blocks):
            if i == 0:
                continue
            else:
                if self.blocks[i-1].hash != block.prev_hash:
                    return False
        return True

    def __len__(self):
        return len(self.blocks)

    @property
    def blocks_count(self):
        return len(self)

    @property
    def tx_count(self):
        return sum([len(b.transactions) for b in self.blocks])

    def __str__(self):
        # return str(self.blocks)
        out = "===============\n"
        out += "chain\n"
        out += "===============\n"

        for b in self.blocks:
            out += str(b)+"\n"
        
        out += "===============\n"
        return out
    

    def __iter__(self):
        for b in self.blocks:
            yield b

    def reviter(self):
        """Iterate the chain in the reverse order."""
        for b in self.blocks[::-1]:
            yield b
