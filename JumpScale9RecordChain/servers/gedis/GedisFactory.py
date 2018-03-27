
# from pprint import pprint as print

from js9 import j

from .GedisServer import GedisServer

JSConfigBase = j.tools.configmanager.base_class_configs


class GedisFactory(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.servers.gedis"
        JSConfigBase.__init__(self, GedisServer)

    def baseclass_get(self):
        return self._child_class

    def _self_class_get(self):
        return GedisFactory

    def start(self, instance="main", background=False):
        s = self.get(instance)
        if background:
            cmd = "js9 '%s.start(instance=\"%s\",background=False)'" % (
                self.__jslocation__, instance)
            j.tools.tmux.execute(cmd, session='main', window='gedisexample',
                                 pane='main', session_reset=False, window_reset=True)
            j.sal.nettools.waitConnectionTest(
                s.config.data["addr"], s.config.data["port"])
        else:
            s = self.get(instance)
            s.start()

    def configure(self, instance="main", port=8889, addr="localhost", secret="", ssl=False, interactive=False, start=False, background=False):
        """
        e.g.
        js9 j.servers.gedisexample.start()'  
        will be different name depending the implementation
        """
        data = {"port": port, "addr": addr, "adminsecret_": secret, "ssl": ssl}
        s = self._child_class(
            instance=instance, data=data, parent=self, interactive=interactive)
        if start:
            s.start(background=background)

    def client_get(self, instance):
        """
        will user server arguments to figure out how to get client, is easy for testing
        """
        c = self.get(instance=instance)
        print(456789)
        from IPython import embed
        embed(colors='Linux')
        ddd
