set -ex
sudo apt install libssl-dev
pip3 install -e .
python3 -c "j.servers.zdb.build()"
python3 -c "from js9 import j;j.tools.jsloader.generate()"
