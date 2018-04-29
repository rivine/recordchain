from js9 import j

#if you want the next secure you can ofcourse do a j.tools.console.ask... to get the secret 
#and not put it in this file, for security, in config file will be encrypted
j.servers.gedis.configure(instance="test", port=5000, addr="127.0.0.1", secret="1234", ssl=False, \
            interactive=False, background=True, start=False)

