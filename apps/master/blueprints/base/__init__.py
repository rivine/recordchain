from flask import Blueprint
from js9 import j

staticpath = j.clients.git.getContentPathFromURLorPath("https://github.com/Jumpscale/web_libs/tree/master/libs")

blueprint = Blueprint(
    'base_blueprint',
    __name__,
    url_prefix='',
    template_folder='templates',
    static_folder=staticpath
)
