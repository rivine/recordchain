
using import "EnumLinkType.capnp".EnumLinkType;
@0xafbfa3088efedefa;

struct Link {
  destdir @0 :UInt32;
  destname @1 :UInt32;
  moddate @2 :UInt32;
  name @3 :Text;
  type @4 :EnumLinkType;
}
