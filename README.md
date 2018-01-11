# recordchain
Chained database which stores users/teams/directory information, also ACL's capnp format on top of [0-db](https://github.com/zero-os/0-db)

![Chain](chain.png)

## Main entities 

### Blockchain
We have 2 separate chains 1 for bdomains and 1 for bobjects


### Bdomain (Blockchain Domain)
BDomains are stored in a blockchain
* id: incremental ID assigned to the domain.
* uid: unique id that stays the same even after modifications 
* name: human readable name for the domain.
* description: domain description
* mod_date: date of modification.
* author: domain creator id (int)
* signature: author signature.
* addr: address given by digital.me
* admins: ids of the admins of this domain.
* hash: (id+moddate+author+name+signature+owners(sorted)+addr+hash previous domain) 


### BObjects
Bobjects stored in their own separate chain
* id: incremental ID assigned to the object.
* uid: unique id that stays the same even after modifications (lookup table how does it practically works?)
* key: secret or key to access the data.
* domain: the domain where the bobject belongs.
* mod_date: date of modification.
* author: domain creator id (int)
* data: capnp data (User/Group/ACL/ACI)
* signature: author signature.
* hash: (id+domain+moddate+author+data+signature+hash previous bobject)
* compression_type: none, blosc, or snappy.
* acl:  link to acl object to allow someone access or not?


#### Types of Data stored in BObjects
##### User
Is stored in a bobject.

* uid: incremental id for user
* alias: list of names relevant to the groups the user is part of.
* key_pub: user public keys used for validation & encryption
* addr: mutable unique address given by the digital.me system
```
  example:
    id: 10    
    addr: "rabbit.luxor.egypt"
    alias:
    - "rabbit"
    - "gouny1"
```
##### Group
Is stored in BObject.

* uid: incremental id for group
* alias:  group names only relevant in all parent groups
* owners: list of owners ids which are people who administer this group and can add/remove users
* key_pub: list of public key which is used for validation & encryption
* addr: mutable unique address given by the digital.me system
```
  example:
    id: 10    
    addr: "rabbitgroup.luxor.egypt"
    owners: [1,2]
    alias:
    - "gig.engineering"
```
##### ACL
Access control list is also stored in bobject.
* uid: incremental id for ACL
* aci: list of ACI (Access Control Item) objects
* hash: md5 hash of concatenation of ACI hashes, used to find this acl to avoid duplicates (needs example)


##### ACI
Access Control Item is stored in BObject

* uid: incremental id for ACI
* groups: list of groups ids (sorted)
* users: list of users ids (sorted)
* right: freely interpreted by ACI users 
    >    text e.g. rwdl- (admin read write delete list -), freely to be chosen
        admin means all rights (e.g. on / = namespace or filesystem level all rights for everything)
        '-' means remove all previous ones (is to stop recursion), if group=0,user=0 then is for all users & all groups
* hash:  md5 of id+groups+users+right