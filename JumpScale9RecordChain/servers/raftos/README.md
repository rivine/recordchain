

# Raft implementation

- based on https://github.com/zhebrak/raftos

you can test by doing 

- js9 'j.servers.raftos_server.test()'

its not working as it should, it sends out the update but doesn't seen to get to consensus, it used to work in other test case.

we need to do the following

- understand this raft fully
- check this implementation
- check how robust it is e.g. what if network gone for while, will it catch up properly if node gets reinserted?
- get it to work & understand the full code, it seems all very well written & well documented

