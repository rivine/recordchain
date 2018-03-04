
using import "EnumBobjectCompressionType.capnp".EnumBobjectCompressionType;
@0xd4bb55bf6f4e1548;

struct Bobject {
  acl @0 :UInt32;
  author @1 :UInt32;
  compressionType @2 :EnumBobjectCompressionType;
  data @3 :Text;
  domain @4 :UInt32;
  hash @5 :Text;
  id @6 :UInt32;
  key @7 :Text;
  moddate @8 :UInt32;
  signature @9 :Text;
  uid @10 :UInt32;
}
