from flask import render_template, redirect, request, url_for
from blueprints.gedis import *
from js9 import j

login_manager = j.servers.web.latest.loader.login_manager

@blueprint.route('/')
def route_default():
    return redirect('/%s/index_.html'%name)


# @login_required
@blueprint.route('/<template>')
def route_template(template):
    return render_template(template)


