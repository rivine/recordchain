
using import "Aci.capnp".Aci;
@0xf03b1ef3820596fe;

struct Acl {
  aci @0 :List(Aci);
  hash @1 :Text;
  uid @2 :Int32;
}
