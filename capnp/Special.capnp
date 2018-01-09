
using import "EnumSpecialType.capnp".EnumSpecialType;
@0xdc779f66beeac41b;

struct Special {
  data @0 :Text;
  moddate @1 :UInt32;
  name @2 :Text;
  type @3 :EnumSpecialType;
}
