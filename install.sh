set -ex
pip3 install -e .
python3 -c "from js9 import j;j.tools.jsloader.generate()"
