import os.path
from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from recordchain.manager import *

app = Flask(__name__)
api = Api(app)

m = Manager()

def jsonify(d):
    return d
    # return dumps(d, default=lambda x: x.__dict__)

chain_backup_path = "/tmp/bchain.dat"

if os.path.exists(chain_backup_path):
    try:
        m.load_chains(chain_backup_path)
    except:
        m.reset_chains()


class BDomainList(Resource):
    def get(self):
        return m.db0domains

    def post(self):
        data = request.json
        tx = m.make_add_bdomain_tx(**data)
        return m.handle_tx(tx)

class BDomain(Resource):
    def get(self, uid):
        return jsonify(m.db0domains[int(uid)])

    def delete(self, uid):
        tx = m.make_delete_bdomain_tx(uid=int(uid))
        return m.handle_tx(tx)


class BObjectList(Resource):

    def get(self):
        return jsonify(m.db0objects)
    
    def post(self):
        data = request.json
        tx = m.make_add_bobject_tx(**data)
        return m.handle_tx(tx)

class BObject(Resource):

    def get(self, uid):
        return m.db0objects[int(uid)]

    def delete(self, uid):
        tx = m.make_delete_bobject_tx(uid=int(uid))
        return m.handle_tx(tx)


class UserList(Resource):
    def get(self):
        return m.users
    
    def post(self):
        data = request.json
        tx = m.make_add_user_tx(**data)
        return m.handle_tx(tx)


class User(Resource):
    def get(self, uid):
        return m.users[int(uid)]

    def delete(self, uid):
        bobject_uid = m.revtable['user_%s'%uid]
        tx = m.make_delete_user_tx(uid=int(bobject_uid), data=dict(uid=uid))
        return m.handle_tx(tx)

    def put(self, uid):
        bobject_uid = m.revtable['user_%s'%uid]

        tx = m.make_update_user_tx(uid=int(bobject_uid), data=dict(uid=uid))
        return m.handle_tx(tx)
 

class GroupList(Resource):
    def get(self):
        return m.groups

    def post(self):
        data = request.json
        tx = m.make_add_group_tx(**data)
        return m.handle_tx(tx)


class Group(Resource):
    def get(self, uid):
        return m.groups[int(uid)]

    def delete(self, uid):
        bobject_uid = m.revtable['group_%s'%uid]

        tx = m.make_delete_group_tx(uid=int(bobject_uid), data=dict(uid=uid))
        return jsonify(m.handle_tx(tx))

    def put(self, uid):
        bobject_uid = m.revtable['group_%s'%uid]

        tx = m.make_update_group_tx(uid=int(bobject_uid), data=dict(uid=uid))
        return jsonify(m.handle_tx(tx))
 

class ACLList(Resource):
    def get(self):
        return jsonify(m.acls)

    def post(self):
        data = request.json
        tx = m.make_add_acl_tx(**data)
        return jsonify(m.handle_tx(tx))

class ACL(Resource):
    def get(self, uid):
        return m.acls[int(uid)]

    def delete(self, uid):
        bobject_uid = m.revtable['acl_%s'%uid]

        tx = m.make_delete_acl_tx(uid=int(bobject_uid), data=dict(uid=uid))
        return jsonify(m.handle_tx(tx))

    def put(self, bobject_uid):
        bobject_uid = m.revtable['acl_%s'%uid]

        tx = m.make_update_acl_tx(uid=int(bobject_uid), data=dict(uid=uid))
        return jsonify(m.handle_tx(tx))
 

class ACIList(Resource):
    def get(self):
        return m.acis

    def post(self):
        data = request.json
        tx = m.make_add_aci_tx(**data)
        return jsonify(m.handle_tx(tx))

class ACI(Resource):
    def get(self, uid):
        return m.acis[int(uid)]

    def delete(self, uid):
        bobject_uid = m.revtable['aci_%s'%uid]

        tx = m.make_delete_aci_tx(uid=int(bobject_uid), data=dict(uid=uid))
        return jsonify(m.handle_tx(tx))

    def put(self, uid):
        bobject_uid = m.revtable['aci_%s'%uid]

        tx = m.make_update_aci_tx(uid=int(bobject_uid), data=dict(uid=uid))
        return jsonify(m.handle_tx(tx))
 

api.add_resource(BDomainList, '/bdomains')
api.add_resource(BDomain, '/bdomains/<uid>')

api.add_resource(BObjectList, '/bobjects')
api.add_resource(BObject, '/bobjects/<uid>')

api.add_resource(UserList, '/users')
api.add_resource(User, '/users/<uid>')

api.add_resource(GroupList, '/groups')
api.add_resource(Group, '/groups/<uid>')


api.add_resource(ACLList, '/acls')
api.add_resource(ACL, '/acls/<uid>')

api.add_resource(ACIList, '/acis')
api.add_resource(ACI, '/acis/<uid>')

if __name__ == "__main__":
    app.run(debug=True)