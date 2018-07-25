from flask import Blueprint

staticpath = j.clients.git.getContentPathFromURLorPath("https://github.com/Jumpscale/web_libs/tree/master/libs")

blueprint = Blueprint(
    'base_blueprint',
    __name__,
    url_prefix='',
    template_folder='templates',
    static_folder=staticpath
)
