from js9 import j

JSConfigBase = j.tools.configmanager.base_class_config

TEMPLATE = """
addr = "127.0.0.1"
port = 8080
"""

SERVER_CODE = """
var http = require('http');
var server = http.createServer();

var Gun = require('gun');
var gun = Gun({web: server});

server.listen(%(port)s, '%(addr)s', function () {
  console.log('Server listening on http://%(addr)s:%(port)s/gun')
})
"""

class GundbServer(JSConfigBase):

    def __init__(self, instance, data={}, parent=None, interactive=True):
        JSConfigBase.__init__(self, instance=instance, data=data,
                              parent=parent, template=TEMPLATE, interactive=interactive)
        self.prefab = j.tools.prefab.local
    
    def install_dep(self):
        """
        Install required dep which includes NodeJs and node module gun
        """
        self.logger.info('installing nodejs')
        self.prefab.runtimes.nodejs.install()
        self.logger.info('installing gun package')
        self.prefab.runtimes.nodejs.npm_install('gun')

    def start(self, location=None):
        """Starts the gundb server in tmux
        
        :param location: where to write the script to start the server, if not specified will be written to /tmp/server.js
        :param location: [type], optional
        """
        if location is None:
            location = j.dirs.TMPDIR + '/server.js'
        j.sal.fs.writeFile(location, SERVER_CODE % self.config.data)
        pm = self.prefab.system.processmanager.get()
        pm.ensure('gun', 'node %s' % location)

    def stop(self):
        """
        Stops the gundb server
        """
        pm = self.prefab.system.processmanager.get()
        pm.stop('gun')
