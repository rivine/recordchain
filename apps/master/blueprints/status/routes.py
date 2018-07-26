from blueprints.status import *
from flask import render_template, send_file
from flask import abort, redirect, url_for

import io

# from flask_login import login_required

from werkzeug.routing import BaseConverter
from js9 import j


@blueprint.route('/index')
@blueprint.route('/')
def index():
    return redirect("%s/status"%name)


@blueprint.route('/<sub>')
def index_sub(sub):
    return render_template('.html')

