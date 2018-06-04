from setuptools import setup, find_packages
from setuptools.command.install import install as _install
from setuptools.command.develop import develop as _develop
import os


def _post_install(libname, libpath):
    from js9 import j
    c = j.core.state.configGet('plugins', defval={})
    c[libname] = "%s/github/rivine/recordchain/JumpScale9RecordChain" % j.dirs.CODEDIR
    j.core.state.configSet('plugins', c)
    j.tools.jsloader.generate()

class install(_install):

    def run(self):
        _install.run(self)
        libname = self.config_vars['dist_name']

        libpath = os.path.join(os.path.dirname(
            os.path.abspath(__file__)),
            libname
        )

        self.execute(
            _post_install,
            (libname, libpath),
            msg="Running post install task"
        )


class develop(_develop):

    def run(self):
        _develop.run(self)
        libname = self.config_vars['dist_name']

        libpath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            libname
        )

        self.execute(
            _post_install,
            (libname, libpath),
            msg="Running post install task"
        )


long_description = ""
try:
    from pypandoc import convert
    long_description = convert('README.md', 'rst')
except ImportError:
    long_description = ""


setup(
    name='JumpScale9RecordChain',
    version='9.3.0',
    description='blockchain tech using jumpscale',
    long_description=long_description,
    url='https://github.com/rivine/recordchain',
    author='GreenItGlobe',
    author_email='info@gig.tech',
    license='Apache',
    packages=find_packages(),
    install_requires=[
        'gevent>=1.2.1',
        'grequests>=0.3.0',
        'msgpack-python>=0.4.8',
        'pudb>=2017.1.2',
        'redis>=2.10.5',
        'requests>=2.13.0',
        'toml>=0.9.2',
        'pynacl>=1.1.2',
        'websockets>=4.0.1',
        'Jinja2==2.10',
        'pyblake2==1.1.2',
        'pycapnp==0.6.3',
        'pyOpenSSL==18.0.0'
    ],
    dependency_links=[
        "git+https://github.com/pyca/pynacl"
    ],
    cmdclass={
        'install': install,
        'develop': develop,
        'development': develop,
    },
)
