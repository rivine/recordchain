@0x93c1ac9f09464fc9;

struct Issue {

    # capnp_schema_get
    state @0 :State;
    enum State {
    new @0;
    ok @1;
    error @2;
    disabled @3;
    }

    #name of actor e.g. node.ssh (role is the first part of it)
    name @1 :Text;
    descr @2 :Text;

}