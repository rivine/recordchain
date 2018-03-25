
from js9 import j
from pprint import pprint as print


TEMPLATE = """
addr = "localhost"
port = 9900
path = ""
mode = ""
id_enable = true
verbose = true
adminsecret_ = ""
"""

JSConfigBase = j.tools.configmanager.base_class_config


class ZDBServer(JSConfigBase):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        """
        """
        JSConfigBase.__init__(self, instance=instance, data=data,
                              parent=parent, template=TEMPLATE, ui=None, interactive=interactive)
        j.sal.fs.createDir(self.config.data["path"])

        if self.config.data["id_enable"]:
            self.config.data["mode"]="direct"

        self._initdir()

    def client_get(self, namespace="default", secret=""):
        return j.clients.zdb.get_by_params(instance=self.instance,
                                           namespace=namespace,
                                           secret=secret,
                                           adminsecret=self.config.data['adminsecret_'],
                                           addr=self.config.data['addr'],
                                           port=self.config.data['port'])


    def _initdir(self):
        root_path = self.config.data['path']
        if root_path == "":
            root_path = j.sal.fs.joinPaths(j.dirs.DATADIR, 'zdb', self.instance)
        # make sure directories exists
        j.sal.fs.createDir(root_path)
        self.root_path = root_path
        

    def start(self):
        """
        start zdb in tmux using this directory (use prefab)
        """

        if self.config.data['id_enable']:
            mode = 'direct'
        else:
            mode = self.config.data['mode']

        j.tools.prefab.local.zero_os.zos_db.start(instance=self.instance,
                                                  host=self.config.data['addr'],
                                                  port=self.config.data['port'],
                                                  index=self.root_path,
                                                  data=self.root_path,
                                                  verbose=self.config.data['verbose'],
                                                  mode=mode,
                                                  adminsecret=self.config.data['adminsecret_'])
        self.logger.info("waiting for zdb server to start on (%s:%s)"%(self.config.data['addr'],self.config.data['port']))
        res = j.sal.nettools.waitConnectionTest(self.config.data['addr'],self.config.data['port'])
        if res is False:
            raise RuntimeError("could not start zdb:'%s' (%s:%s)"%self.instance,self.config.data['addr'],self.config.data['port'])

    def stop(self):
        j.tools.prefab.local.zero_os.zos_db.stop(self.instance)

    def destroy(self):
        j.sal.fs.removeDirTree(self.root_path)
        ipath = j.dirs.VARDIR + "/zdb/index/%s.db"%self.instance
        j.sal.fs.remove(ipath)
        self._initdir()
