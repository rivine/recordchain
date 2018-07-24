## install record chain

```bash

##OPTIONAL IF UBUNTU
#apt install libssl-dev`

#install recordchain 
js9_code get --url="git@github.com:rivine/recordchain.git"
cd $HOMEDIR/code/github/rivine/recordchain
sh install.sh

```

## build zdb

```bash
#build zdb
js9 'j.servers.zdb.build()'
```
