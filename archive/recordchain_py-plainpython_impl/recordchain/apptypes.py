from hashlib import md5
import datetime

def filter_dict(d, wanted_keys):
    return {k: d[k] for k in set(wanted_keys) & set(d.keys())}

### Application types: also used for marshaling/unmarshaling dicts. 
class BDomain(object):

    def __init__(self, uid=None, name="bdomain", description="", author_id="", signature="mysig", admins=None, addr="", prev_hash=""):
        """
  blockchain domain
    id: is increment id for any domain in a blockchain, is stored in itself in bdomain 1 (always) type: number
    uid: is unique id which stays the same even after mods type: number
    moddate: last modification date type: number
    author: id of author who created this bobject type: number
    name: name of the domain, needs to be unique
    description: freely to be given description by owner of the domain type: string      
    signature: signature done by digital.me private key of author (8 bytes) type: string    
    admins: list of owners which are people who administer this domain type: number[]
    addr: is the address given by the digital.me system, is for the master of this blockchain type: string        
    hash: md5 of (id+moddate+author+name+signature+owners(sorted)+addr+hash previous message) type: string
        """
        admins = admins or []
        self.id = None
        self.uid = uid
        self.author = author_id
        self.name = name
        self.description = description
        self.signature = signature 
        self.addr = ""
        self._hash = ""
        self.mod_date = 0
        self.prev_hash = ""
        self.owners = sorted(admins)

    def to_dict(self):
        wanted_keys = set('id', 'uid', 'author', 'name', 'description', 'signature', 'addr', 'prev_hash', 'owners')
        return filter_dict(self.__dict__, wanted_keys)

    def seal(self):
        self.mod_date = datetime.datetime.now()
        self._hash = md5("".join(map(str, [self.id, self.mod_date, self.author, self.name, self.signature, self.owners, self.addr,self.prev_hash])).encode()).hexdigest()
    
    @property
    def hash(self):
        return self._hash

    def __str__(self):
        return "<BDomain {} {}>".format(self.name, self.uid)
    
    __repr__ = __str__



class BObject:

    def __init__(self, uid=None, key="", name="", domain_uid="domain_uid", author_id="", data="", signature="", compression_type="none", acl="", prev_hash=""):
        """
  blockchain object
    id: is incremental id for any object in a blockchain, unique for all changes type: number
    uid: is unique id which stays the same even after mods, there needs to be lookup table type: number
    key: secret or key, can be used to give someone access to data of this obj, max 32 bytes type: string       
    domain: is unique id for the domain in which this bobject lives e.g. user.system type: number 
    moddate: last modification date type: number
    author: id of author who created this bobject type: number
    data: the capnp data type: string
    signature: signature done by digital.me private key of author (8 bytes) type: string
    hash: md5 of (id+domain+moddate+author+data+signature+hash previous message) type: string
    compression_type: is the compression type of the message, if not specified then non compressed enum: [ none, blosc, snappy ]
    acl: link to acl object to allow someone access or not type: number
  example:
    id: 10    
    name: "Rabbit From Egypt"
    digitalme_url: "rabbit.luxor.egypt"
    alias:
    - "rabbit"
    - "gouny1"
    compression_type: "blosc"
    addr: "192.168.1.1"

        """
        self.id = None
        self.uid = uid
        self.name = name
        self.key = key
        self.domain_uid = domain_uid
        self.author = author_id
        self.signature = signature
        self.compression_type = compression_type
        self.acl = acl # link to ACL : TODO.
        self.data = data
        self._hash = None
        self.prev_hash = prev_hash
    
    def to_dict(self):
        wanted_keys = set('id', 'uid', 'author', 'name', 'key', 'signature', 'domain_uid', 'addr', 'prev_hash', 'data', 'acl')
        return filter_dict(self.__dict__, wanted_keys)

    def seal(self):
        self.mod_date = datetime.datetime.now()
        self._hash = md5("".join(map(str, [self.id, self.domain_uid, self.mod_date, self.author, self.data, self.signature, self.prev_hash])).encode()).hexdigest()
    
    @property
    def hash(self):
        return self._hash

    def __str__(self):
        return "<BObject {} {}_{} on domain {} with data {}>".format(self.name, self.id, self.uid, self.domain_uid, self.data)


### DATA MODELS SAVED IN BOBJECTS.
class User:
    def __init__(self, uid=None, alias="", key_pub="", addr=""):
        """
        user:
        uid:  unique id for a user, increments type: number
            
        alias: chosen name(s), does not have to be unique, public readable, only relevant in all groups you are part off. type: string[]
        key_pub: public key which is used for validation & encryption type: string[]
        addr: is the address given by the digital.me system, is unique per user & can change type: string
        """
        self.uid = uid
        self.alias = alias
        alias_addr = None
        if isinstance(alias, str):
            alias_addr = alias
        elif isinstance(alias, list):
            alias_addr = alias[0]
        self.addr = alias_addr + ".user.digital"  

        self.key_pub = ""

    def to_dict(self):
        wanted_keys = set('id', 'alias', 'addr', 'key_pub')

        return filter_dict(self.__dict__, wanted_keys)
 

# WHAT IS THE RELATION BETWEEN USERS AND GROUPS? 
class Group:
    def __init__(self, uid=None, alias="", owners=None, key_pub="", addr=""):
        """
        group:
            uid: is unique id for a group, increments type: number
            alias: chosen name(s), does not have to be unique, public readable, only relevant in all parent groups type: string[]
            owners: list of owners which are people who administer this group and can add/remove users type: number[]
            key_pub: public key which is used for validation & encryption type: string[]
            addr: is the address given by the digital.me system, is unique per group & can change type: string
        example:
            id: 10    
            addr: "rabbitgroup.luxor.egypt"
            owners: [1,2]
            alias:
            - "gig.engineering"

        """

        self.uid = uid 
        self.alias = alias

        alias_addr = None
        if isinstance(alias, str):
            alias_addr = alias
        elif isinstance(alias, list):
            alias_addr = alias[0]
        self.addr = alias_addr + ".user.digital"  
        
        self.key_pub = ""
        self.owners = owners or []
        self.addr = alias + ".group.digital"

    def to_dict(self):
        wanted_keys = set('uid', 'alias', 'addr', 'key_pub', 'owners')
        return filter_dict(self.__dict__, wanted_keys)

class ACL:
    uid = 0
    def __init__(self, uid=None, aci=None):
        """
    uid: is unique id for the acl, increments type: number
    aci: list of access control items type: ACI[]
    hash: description: md5 hash of concatenation of ACI hashes, used to find this acl to avoid duplicates type: text      
        """
        self.uid = None 
        self.aci = sorted(aci) or None

    @property
    def hash(self):
        return md5(str(self.aci).encode()).hexdigest()
        
    def to_dict(self):
        wanted_keys = set('uid', 'aci')
        return filter_dict(self.__dict__, wanted_keys)

class ACI:
    def __init__(self, uid=None, groups=None, users=None, right=""):
        """
    uid: is unique id for the acl, increments type: number
    groups: link to group(s) type: number[]
    users: link to user(s) type: number[]
    right:
      description: |
        text e.g. rwdl- (admin read write delete list -), freely to be chosen
        admin means all rights (e.g. on / = namespace or filesystem level all rights for everything)
        '-' means remove all previous ones (is to stop recursion), if group=0,user=0 then is for all users & all groups
    hash: md5 hash of id+sorted_groups+sorted_users+right, used to make sure we only link acl once type: text
        """
        self.uid = uid 
        self.groups = sorted(groups) or []
        self.users = sorted(users) or []
        self.right = ""

    @property
    def hash(self):
        return md5("".join(map(str, [self.uid, self.groups, self.users, self.right])).encode())

    def to_dict(self):
        wanted_keys = set('uid', 'groups', 'users', 'right')

        return filter_dict(self.__dict__, wanted_keys)