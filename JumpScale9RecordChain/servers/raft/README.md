# Raft

This implementation of raft is using pysyncobj

It is a highly effective library, quite high level so maybe more difficult to understand how the raft exactly works.

While testing on my mac OSX I could not get it to work stable.
When killing nodes, the catchup did not work well.

we need to test this implementation well, come up with strategies where we have lots of load & kill nodes.
Do up to 30 nodes, see what happens if random nodes get killed.
Ofcourse test very well for 3 too because its easier to spot issues.


