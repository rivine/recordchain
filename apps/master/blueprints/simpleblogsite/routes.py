from flask import render_template, redirect, request, url_for
from blueprints.simpleblogsite import *
from js9 import j

login_manager = j.servers.web.latest.loader.login_manager

j.tools.docgenerator.load("https://github.com/Jumpscale/web_libs/tree/master/docsites_examples/simpleblogsite")
ds = j.tools.docgenerator.docsite_get("simpleblogsite")

@blueprint.route('/')
def route_default():
    # return redirect(url_for('index_.html'))
    return redirect('/%s/index.html'%name)

@blueprint.route('/blog/<page>.html')
@blueprint.route('/blog/<page>')
def route_blog(page):
    # doc = ds.doc_get(page,cat="blog")
    return render_template('%s_%s.html'%(name, page))


# # ds.doc_get(template)
# # @login_required
# @blueprint.route('/<template>.html')
# def route_template(template):
#     # from IPython import embed;embed(colors='Linux')
#     return render_template('%s_%s.html'%(name,template))

