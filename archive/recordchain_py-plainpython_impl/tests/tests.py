from recordchain import *


class Author:
    def __init__(self, id, name):
        self.id=id
        self.name = name
        self.privkey, self.pubkey, _, _ = generate_keys(self.name)

authors = [Author(0, "ahmed"), Author(1, "ali"), Author(2, "abdu")]
authorsid = [author.id for author in authors]


def faketestdomains():
    testdomains = []
    testdomains.append(BDomain(name='cs.egypt', description="eg office", signature="cssig", admins=[0]))
    testdomains.append(BDomain(name='gig.be', description="be office", signature="besig", admins=[1]))
    testdomains.append(BDomain(name='gig.uk', description="uk office", signature="uksig", admins=[2, 1]))
    return testdomains


def fakeusers():
    def gen_user(addr_fmt="%s.system.eg"):
        name = "user%d"%i
        _, pub, _, _ = generate_keys(name)
        return User(None, name, pub, addr_fmt.format(name))

    users = []
    for i in range(2):
        users.append(gen_user())
    for i in range(2):
        users.append(gen_user("%s.system.be"))
    return users


def fakegroups():
    groups = []
    groups.append(Group(None, 'engineers_eg', [1], "gigengineering pubkey", "gig.engineering.eg"))
    groups.append(Group(None, 'salesmasters', [2,3], "sales pubkey", "sales.gig.be"))
    return groups

def fakeacis():
    acis = []
    acis.append(ACI(groups=[0], users=[0,2], right="rw"))
    acis.append(ACI(groups=[1,2], users=[1,], right="r"))
    acis.append(ACI(groups=[0], users=[0,1], right="rw"))
    acis.append(ACI(groups=[0], users=[2], right="r"))

    return acis

def fakeacls():
    acis = fakeacis()
    acls = []
    # fan control (aci 0, 1)
    acls.append(ACL(aci=[0,1]))
    # router access (aci 2, 3)
    acls.append(ACL(aci=[2,3]))

    return acls


def faketestbobjects():
    testbobjects = []
    testbobjects.append(BObject(author_id=1, data="", name="first obj"))
    testbobjects.append(BObject(author_id=2, data="", key="magickey", name="second obj"))
    testbobjects.append(BObject(author_id=1, data="", name="third obj"))
    return testbobjects


def test_chain_validity():
    bc = Blockchain()
    bc.add(BDomain(name='codescalers.egypt'))
    bc.add(BDomain(name='gig.ghent'))
    bc.add(BDomain(name='gig.uk'))
    assert bc.is_valid() == True
    bc.blocks.append(BDomain('invalidone'))
    assert bc.is_valid() == False



def test_add_bdomains():
    m = Manager()
    tx_add1 = m.make_add_bdomain_tx(name="codescalers.egypt")
    tx_add2 = m.make_add_bdomain_tx(name="gig.uk")
    tx_add3 = m.make_add_bdomain_tx(name="gig.be")
    m.handle_tx(tx_add1)
    m.handle_tx(tx_add2)
    m.handle_tx(tx_add3)

    assert m.bdomainschain.tx_count == 3
    print(m.bdomainschain)


def test_add_invalid_bdomains():
    m = Manager()
    tx_add1 = m.make_add_bdomain_tx(name="codescalers.egypt")
    tx_add2 = m.make_add_bdomain_tx(name="gig.uk")
    tx_add3 = m.make_add_bdomain_tx(name="gig.be")
    tx_add4 = m.make_add_bdomain_tx(unsupported_param="gig.be") 
    m.handle_tx(tx_add1)
    m.handle_tx(tx_add2)
    m.handle_tx(tx_add3)
    m.handle_tx(tx_add4)  # REJECTED 

    assert m.bdomainschain.tx_count == 3
    print(m.bdomainschain)

def test_add_delete_bdomains():
    m = Manager()
    tx_add1 = m.make_add_bdomain_tx(name="codescalers.egypt")
    tx_add2 = m.make_add_bdomain_tx(name="gig.uk")
    tx_add3 = m.make_add_bdomain_tx(name="gig.be")
    m.handle_tx(tx_add1)
    m.handle_tx(tx_add2)
    m.handle_tx(tx_add3)

    assert m.bdomainschain.tx_count == 3

    tx_delete1 = m.make_delete_bdomain_tx(uid=1)
    m.handle_tx(tx_delete1)

    assert m.bdomainschain.tx_count == 4
    assert len(m.db0domains) == 2

    print(m.bdomainschain)

def test_add_update_bdomains():
    m = Manager()
    tx_add1 = m.make_add_bdomain_tx(name="codescalers.egypt")
    tx_add2 = m.make_add_bdomain_tx(name="gig.uk")
    tx_add3 = m.make_add_bdomain_tx(name="gig.be")
    m.handle_tx(tx_add1)
    m.handle_tx(tx_add2)
    m.handle_tx(tx_add3)
    assert m.bdomainschain.tx_count == 3

    tx_delete1 = m.make_delete_bdomain_tx(uid=3)
    m.handle_tx(tx_delete1)
    assert m.bdomainschain.tx_count == 4

    tx_update1 = m.make_update_bdomain_tx(uid=1, name="cs.egy")
    m.handle_tx(tx_update1)
    assert m.bdomainschain.tx_count == 5
    assert len(m.db0domains) == 2

    print(m.bdomainschain)

## bobjects tests
def test_add_bobjects():
    m = Manager()
    tx_add1 = m.make_add_bobject_tx(author_id=1, data="", name="first obj")
    tx_add2 = m.make_add_bobject_tx(author_id=2, data="", key="magickey", name="2nd obj")
    tx_add3 = m.make_add_bobject_tx(author_id=1, data="", name="3rd obj")
    m.handle_tx(tx_add1)
    m.handle_tx(tx_add2)
    m.handle_tx(tx_add3)
    assert m.bobjectschain.tx_count == 3

    print(m.bobjectschain)

def test_add_delete_bobjects():
    m = Manager()
    tx_add1 = m.make_add_bobject_tx(author_id=1, data="", name="first obj")
    tx_add2 = m.make_add_bobject_tx(author_id=2, data="", key="magickey", name="2nd obj")
    tx_add3 = m.make_add_bobject_tx(author_id=1, data="", name="3rd obj")
    m.handle_tx(tx_add1)
    m.handle_tx(tx_add2)
    m.handle_tx(tx_add3)
    assert m.bobjectschain.tx_count == 3
    tx_delete1 = m.make_delete_bobject_tx(uid=1)
    m.handle_tx(tx_delete1)

    assert m.bobjectschain.tx_count == 4
    assert len(m.db0objects) == 2

    print(m.bobjectschain)

def test_add_update_bobjects():
    m = Manager()
    tx_add1 = m.make_add_bobject_tx(author_id=1, data="", name="first obj")
    tx_add2 = m.make_add_bobject_tx(author_id=2, data="", key="magickey", name="2nd obj")
    tx_add3 = m.make_add_bobject_tx(author_id=1, data="", name="3rd obj")
    m.handle_tx(tx_add1)
    m.handle_tx(tx_add2)
    m.handle_tx(tx_add3)
    assert m.bobjectschain.tx_count == 3
    tx_delete1 = m.make_delete_bobject_tx(uid=1)
    m.handle_tx(tx_delete1)
    assert m.bobjectschain.tx_count == 4


    tx_update1 = m.make_update_bobject_tx(uid=3, name="updated name")

    m.handle_tx(tx_update1)
    assert m.bobjectschain.tx_count == 5
    assert len(m.db0objects) == 2

    print(m.bobjectschain)



## test users.
def test_add_users():
    users = fakeusers()
    txs = []
    m = Manager()

    for i, u in enumerate(users):
        tx = m.make_add_user_tx(author_id=1, name="obj%d"%i, data=dict(uid=u.uid, addr=u.addr, alias=[u.alias]))
        txs.append(tx)

    for tx in txs:
        m.handle_tx(tx)   

    assert m.bobjectschain.tx_count == len(users)


def test_add_groups():
    groups = fakegroups()
    txs = []
    m = Manager()

    for i, g in enumerate(groups):
        tx = m.make_add_group_tx(author_id=1, name="obj%d"%i, data=dict(uid=g.uid, addr=g.addr, alias=[g.alias]))
        txs.append(tx)

    for tx in txs:
        m.handle_tx(tx)   

    assert m.bobjectschain.tx_count == len(groups)

def test_add_users_groups():
    users = fakeusers()
    groups = fakegroups()
    txs = []
    m = Manager()

    for i, g in enumerate(groups):
        tx = m.make_add_group_tx(author_id=1, name="obj%d"%i, data=dict(uid=g.uid, addr=g.addr, alias=[g.alias]))
        txs.append(tx)

    for i, u in enumerate(users):
        tx = m.make_add_user_tx(author_id=1, name="obj%d"%i, data=dict(uid=u.uid, addr=u.addr, alias=[u.alias]))
        txs.append(tx)

    for tx in txs:
        m.handle_tx(tx)   

    assert m.bobjectschain.tx_count == len(groups) + len(users)


def test_add_remove_users_groups():
    users = fakeusers()
    groups = fakegroups()
    txs = []
    m = Manager()


    for i, g in enumerate(groups):
        tx = m.make_add_group_tx(author_id=1, name="obj%d"%i, data=dict(uid=g.uid, addr=g.addr, alias=[g.alias]))
        m.handle_tx(tx)

    for i, u in enumerate(users):
        tx = m.make_add_user_tx(author_id=1, name="obj%d"%i, data=dict(uid=u.uid, addr=u.addr, alias=[u.alias]))
        m.handle_tx(tx)

    assert m.bobjectschain.tx_count == len(groups) + len(users)
    assert len(groups) + len(users) == len(m.users) + len(m.groups)
    
    m.summary()

    ## NOW WE REMOVE A USER
    auserid = list(m.users.keys())[0]    
    bobjuid = m.revtable["user_%d"%auserid]
    tx = m.make_delete_user_tx(uid=bobjuid, data=dict(uid=auserid))
    m.handle_tx(tx)
    assert len(groups) + len(users) == len(m.users) + len(m.groups) + 1

    m.summary()


def test_add_acl():
    users = fakeusers()
    groups = fakegroups()
    acis = fakeacis()
    acls = fakeacls()
    txs = []
    m = Manager()

    for i, g in enumerate(groups):
        tx = m.make_add_group_tx(author_id=1, name="obj%d"%i, data=dict(uid=g.uid, addr=g.addr, alias=[g.alias]))
        txs.append(tx)

    for i, u in enumerate(users):
        tx = m.make_add_user_tx(author_id=1, name="obj%d"%i, data=dict(uid=u.uid, addr=u.addr, alias=[u.alias]))
        txs.append(tx)


    for i, a in enumerate(acis):
        tx = m.make_add_aci_tx(author_id=1, name="obj%d"%i, data=dict(uid=a.uid, groups=a.groups, users=a.users, hash=a.hash))
        txs.append(tx)
    
    
    for i, a in enumerate(acls):
        tx = m.make_add_acl_tx(author_id=1, name="obj%d"%i, data=dict(uid=a.uid, aci=a.aci, hash=a.hash))
        txs.append(tx)
    

    for tx in txs:
        m.handle_tx(tx)   


    assert m.bobjectschain.tx_count == sum(map(len, [users,groups, acis, acls]))
    print(m.bobjectschain)


def test_add_update_user():
    users = fakeusers()
    u = users[0]
    m = Manager()

    tx = m.make_add_user_tx(author_id=1, name="obj_user", data=dict(uid=u.uid, addr=u.addr, alias=[u.alias]))
    bobj_uid = m.handle_tx(tx)   

    print(m.bobjectschain)

    tx = m.make_update_user_tx(uid=bobj_uid, data=dict(uid=u.uid, addr=u.addr, alias=["updated_alias_name"]))
    m.handle_tx(tx)
    print(m.bobjectschain)

## test chain load/dump
def test_dump_load_chains():
    m = Manager()
    tx_add1 = m.make_add_bobject_tx(author_id=1, data="", name="first obj")
    tx_add2 = m.make_add_bobject_tx(author_id=2, data="", key="magickey", name="2nd obj")
    tx_add3 = m.make_add_bobject_tx(author_id=1, data="", name="3rd obj")
    m.handle_tx(tx_add1)
    m.handle_tx(tx_add2)
    m.handle_tx(tx_add3)

    assert m.bobjectschain.tx_count == 3
    tx_delete1 = m.make_delete_bobject_tx(uid=1)
    m.handle_tx(tx_delete1)
    assert m.bobjectschain.tx_count == 4

    tx_update1 = m.make_update_bobject_tx(uid=3, name="updated name")

    m.handle_tx(tx_update1)
    assert m.bobjectschain.tx_count == 5
    assert len(m.db0objects) == 2 

    m.save_chains("/tmp/chains_dump.dat")
    m.bdomainschain = None 
    m.bobjectschain = None
    m.load_chains("/tmp/chains_dump.dat")
    assert m.bobjectschain.tx_count == 5
    assert len(m.db0objects) == 2 
    print(m.bobjectschain)