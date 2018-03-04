
from js9 import j
from pprint import pprint as print


TEMPLATE = """
addr = "localhost"
port = 9900
path = ""
key_enable = false
id_enable = true
verbose = true
"""

JSConfigBase = j.tools.configmanager.base_class_config


class ZDBServer(JSConfigBase):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        """
        """
        JSConfigBase.__init__(self, instance=instance, data=data,
                              parent=parent, template=TEMPLATE, ui=None, interactive=interactive)
        j.sal.fs.createDir(self.config.data["path"])

        if self.config.data["key_enable"] and self.config.data["id_enabled"]:
            raise RuntimeError("have to choose or using id or using key")

    @property
    def client(self):
        return j.data.zdb.get_by_params(instance=self.instance,
                                        # secret=self.config.data['secret_'], # re-enable once configure creates the namepsace and it protected by password
                                        path=self.config.data['path'],
                                        addr=self.config.data['addr'],
                                        port=self.config.data['port'])

    def configure(self, maxsize=0):
        """configure the ZDB namespace (identified by secret)

        Keyword Arguments:
            maxsize {int} -- size in MBytes (default: {0})
        """
        # TODO: *1
        # depends on : https://github.com/zero-os/0-db/issues/5
        pass

    def start(self):
        """
        start zdb in tmux using this directory (use prefab)
        """
        root_path = self.config.data['path']
        if root_path == "":
            root_path = j.sal.fs.joinPaths(j.dirs.DATADIR, 'zdb', self.instance)
        # make sure directories exists
        j.sal.fs.createDir(root_path)

        if self.config.data['key_enable'] and self.config.data['id_enable']:
            raise j.exceptions.Input("key_enable and id_enable cannot be both true")
        if self.config.data['key_enable'] is False and self.config.data['id_enable'] is False:
            raise j.exceptions.Input("key_enable and id_enable cannot be both false")

        if self.config.data['key_enable']:
            mode = 'user'
        elif self.config.data['id_enable']:
            mode = 'direct'
        else:
            j.exceptions.Input("can't determine which mode of 0-db to run")

        j.tools.prefab.local.zero_os.zos_db.start(instance=self.instance,
                                                  host=self.config.data['addr'],
                                                  port=self.config.data['port'],
                                                  index=root_path,
                                                  data=root_path,
                                                  verbose=self.config.data['verbose'],
                                                  mode=mode)

    def stop(self):
        j.tools.prefab.local.zero_os.zos_db.stop(self.instance)

    @property
    def sizeMB(self):
        pass
        # TODO:*1
